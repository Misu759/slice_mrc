from typing import List, Tuple
import copy

from topology import Topology
from overlay_topology import OverlayTopology
from multiple_routing_configurations import MultipleRoutingConfigurations
from constants import DIRECTORY_NAME, BACKUP_CONF_NUM
import path_strings_collection as path_str


class TopologyManager(object):
  def __init__(self) -> None:
    pass

  def extract_slice_from_substrate_topo(self, substrate_adj_matrix: List[int], slice_nodes: List[int]) -> List[int]:
    '''
    任意のスライスに対して，基盤ネットワークからグラフを抜き取る．

    :params substrate_adj_matrix List[int]: 物理ネットワークの隣接行列（２次元配列）
    :params silce_nodes List[int]: スライスに対応した物理ネットワーク上のノード番号
    :return slice_adj_matrix List[int]: オーバーレイネットワークのノード番号．ノード番号は基盤ネットワークのノード番号が若い順になる．
    '''
    slice_adj_list = [[] for i in range(len(slice_nodes))]
    for i in range(len(slice_nodes)):
      for j in range(len(slice_nodes)):
        if substrate_adj_matrix[slice_nodes[i]][slice_nodes[j]] == 1:
          slice_adj_list[i].append(j)
    
    slice_adj_matrix = [[0 for i in range(len(slice_nodes))] for j in range(len(slice_nodes))]
    for i, adj_nodes_list in enumerate(slice_adj_list):
      for j in adj_nodes_list:
        slice_adj_matrix[i][j] = 1

    return slice_adj_matrix
  

  def calculate_shotest_path_on_substrate(self, substrate_dist_matrix: List[int], slice_nodes: List[int], slice_dist_matrix: List[int]) -> Tuple[int, int]:
    '''
    物理ネットワーク上にスライスに対応するノード間で最短経路を見つける

    :params substrate_dist_matrix List[int]: 物理ネットワークのホップ数が格納された隣接行列
    :params silce_nodes List[int]: スライスに対応した物理ネットワークのノード番号
    :params slice_dist_matrix List[int]: オーバーレイネットワークのホップ数が格納された隣接行列
    :return (connect_src, connect_dst) Tuple[int, int]: 最短経路を持つノード番号のペア（物理ネットワークのノード番号）
    '''
    # 初期値
    shortest_path = 100
    # 物理ネットワーク上で，オーバーレイネットワークに対応するノード間の最短経路を求める
    slice_nodes_num = len(slice_nodes)
    for i in range(slice_nodes_num):
      src = slice_nodes[i]
      for j in range(i + 1, slice_nodes_num):
        dst = slice_nodes[j]
        if slice_dist_matrix[i][j] < 0 and 1 <= substrate_dist_matrix[src][dst] <= shortest_path:
          shortest_path = substrate_dist_matrix[src][dst]
          connect_src = src
          connect_dst = dst
  
    return connect_src, connect_dst
  


  def generate_overlay_network(self, substrate_adj_matrix: List[int], slice_nodes: List[int]) -> List[int]:
    '''
    物理ネットワーク上の任意のノードからオーバーレイネットワーク（スライス）を作成する

    :params substrate_adj_matrix List[int]: 物理ネットワークの隣接行列（２次元配列）
    :params silce_nodes List[int]: スライスに対応した物理ネットワーク上のノード番号
    :return overlay_network OverlayNetwork: 与えられたスライスから作成したオーバーレイネットワーククラスのインスタンス
    '''
    slice_adj_matrix = self.extract_slice_from_substrate_topo(substrate_adj_matrix, slice_nodes)
    
    # overlay_nodes_on_substrate_network, overlay_adj_matrix = self.connect_overlay_topology(substrate_adj_matrix, slice_nodes, slice_adj_matrix)

    overlay_topology = OverlayTopology(slice_adj_matrix, slice_nodes, substrate_adj_matrix)

    return overlay_topology

  def _update_dfs_tree(self, topology: Topology) -> None:
    '''
    次の探索に備えて前回の探索で作成したDFS木の情報を初期値に戻す

    :params topology Topology: DFS対象のトポロジー
    '''
    topology.dfs_tree.search_count = 0
    topology.dfs_tree.isVisited = [False] * (len(topology.adj_matrix))
    topology.dfs_tree.parent = [-1] * (len(topology.adj_matrix))


  def find_articulation_points(self, topology: Topology, start_point: int = 0) -> List[int]:
    '''
    :return articulation_points_list List[int] オーバーレイネットワークの関節点のノード番号（物理ネットワークとは紐づいていない）
    '''
    self._update_dfs_tree(topology)
    topology.dfs_tree.depth_first_search(start_point, topology.adj_list)

    node_num = len(topology.adj_matrix)
    for i in range(node_num):
      if topology.dfs_tree.isVisited[i] == False:
        topology.dfs_tree.depth_first_search(i, topology.adj_list)
    
    articulation_points_list = []
    for index, value in enumerate(topology.dfs_tree.isArticulation_point):
      if value == True:
        articulation_points_list.append(index)
    
    return articulation_points_list
  

  def apply_mrc(self, mrc_subject_adj_matrix: List[int], output_file_name: str, start_point: int =0) -> MultipleRoutingConfigurations:

    mrc = MultipleRoutingConfigurations(mrc_subject_adj_matrix)
    
    mrc.node_queue.put(start_point)

    for i in range(len(mrc_subject_adj_matrix)):
      if i != start_point:
        mrc.node_queue.put(i)
    
    conf_isolating = 0
    node_num = len(mrc_subject_adj_matrix)

    while not mrc.node_queue.empty():
      # キューから順番に取り出して分離していく
      node_try_to_isolate = mrc.node_queue.get()

      conf_to_start_search = conf_isolating
      while True:
        # 通常ノードのみで構成されたグラフをコピー
        copy_normal_nodes_matrix = copy.deepcopy(mrc.backup_conf[conf_isolating].normal_nodes_matrix)
        
        # 隣接ノード間のリンクを切断
        for i in range(node_num):
          copy_normal_nodes_matrix[node_try_to_isolate][i] = 0
          copy_normal_nodes_matrix[i][node_try_to_isolate] = 0

        if mrc.backup_conf[conf_isolating].can_isolate_a_node(copy_normal_nodes_matrix, node_try_to_isolate):
          # TODO 修正必要          
          was_able_to_isolate = mrc.isolate_a_node(conf_isolating, node_try_to_isolate)
          if was_able_to_isolate == True:
            
            mrc.backup_conf[conf_isolating].isolated_nodes_set.add(node_try_to_isolate)
            
            # 通常ノードのみで構成するグラフの要素から分離ノードに隣接する要素を削除
            for i in range(node_num):
              mrc.backup_conf[conf_isolating].normal_nodes_matrix[node_try_to_isolate][i] = 0
              mrc.backup_conf[conf_isolating].normal_nodes_matrix[i][node_try_to_isolate] = 0
            
            conf_isolating = (conf_isolating +1) % BACKUP_CONF_NUM
            # TODO 何してるのか思い出す
            mrc.get_link_queue_for_sorting(conf_isolating)
            break

        # print('Node' + str(node_try_to_isolate) + 'can\'t isolate in conf' + str(conf_isolating))
        conf_isolating = (conf_isolating +1) % BACKUP_CONF_NUM

        if conf_to_start_search == conf_isolating:
          break
      
      #ノードがどの構成で分離されているかの確認
      for i in range(BACKUP_CONF_NUM):
        if node_try_to_isolate in set(mrc.backup_conf[i].isolated_nodes_set):
          # print("Node" + str(node_try_to_isolate) +"is isolated in configuration" + str(i) + "\n")
          break
      else:
        # print("Failed to isolate node" + str(node_try_to_isolate) + "\n")
        
        # 円状のトポロジーに対応するために加えた
        # TODO いるか確かめてから修正
        return False

    # mrc.export_adj_matrix(output_file_name)

    # TODO Create and read a list of sets insted of reading from a file
    # for conf_i in range(len(mrc.backup_conf)):
    #   with open(path_str.isolate_nodes_set_file + str(conf_i) + ".txt", 'w') as f:
    #     f.write(",".join(map(str, list(mrc.backup_conf[conf_i].isolated_nodes_set))))
            
    return mrc
