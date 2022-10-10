from typing import List, Tuple, Dict
import copy
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra

from overlay_topology import OverlayTopology
from topology_manager import TopologyManager

import sys

class TopologyChanger(object):
  def __init__(self) -> None:
    pass

  def _add_slice_node(self, overlay_topology: OverlayTopology, connect_src: int, connect_dst: int, dist_matrix: List[int], predecessors: List[int]) -> None:
    '''
    物理ネットワーク上に指定した2点間の最短経路を求めて, スライスのリストに追加する
    '''
    slice_nodes = copy.deepcopy(overlay_topology.node_list_mapping_to_substrate)

    dst = connect_dst
    for _ in range(dist_matrix[connect_src][connect_dst]):
        slice_nodes.append(predecessors[connect_src][dst])
        dst = predecessors[connect_src][dst]

    slice_nodes = list(set(slice_nodes))
    slice_nodes.sort()

    overlay_topology.node_list_mapping_to_substrate = slice_nodes

    return None
  

  def connect_overlay_topology(self, overlay_topology: OverlayTopology, topology_manager: TopologyManager, reconnect: bool = False) -> None:
    '''
    オーバーレイトポロジーにノードを追加する
    
    物理ネットワーク上の最短経路を求め，その経路上のノードをトポロジーに追加する

    :params overlay_topology OverlayTopology: 対象となるオーバーレイトポロジー
    :params topology_manager TopologyManager
    :params reconnect bool: Trueを指定した場合はオーバーレイ上で使われていないリソースを使用して接続する
    '''
    if reconnect:
      substrate_csr__matrix = csr_matrix(overlay_topology.substrate_adj_matrix_without_overlay)
    else:
      substrate_csr__matrix = csr_matrix(overlay_topology.substrate_adj_matrix)
    # dist_matrix グラフ上の2点間のホップ数
    # predeccessors 最終ホップのノード番号
    substrate_dist_matrix, substrate_predecessors = dijkstra(csgraph=substrate_csr__matrix, directed=False, return_predecessors=True)
    substrate_dist_matrix = substrate_dist_matrix.astype(int)

    while True:
      slice_adj_csr_matrix = csr_matrix(overlay_topology.adj_matrix)
      slice_dist_matrix = dijkstra(csgraph=slice_adj_csr_matrix, directed=False).astype(int)

      # 全ノード間で接続性がある場合，ループ処理を抜ける
      # nupmyのdist_matrixをint型に変換すると，接続性のないノード間には「-9223372036854775808」が入っている
      if np.all(slice_dist_matrix >= 0):
        break
      connect_src, connect_dst = topology_manager.calculate_shotest_path_on_substrate(substrate_dist_matrix, overlay_topology.node_list_mapping_to_substrate, slice_dist_matrix)
      
      self._add_slice_node(overlay_topology, connect_src, connect_dst, substrate_dist_matrix, substrate_predecessors)
      
      slice_adj_matrix = topology_manager.extract_slice_from_substrate_topo(overlay_topology.substrate_adj_matrix, overlay_topology.node_list_mapping_to_substrate)
      overlay_topology.adj_matrix = slice_adj_matrix

      overlay_topology.update_attribute()
      
    return None
  

  def _get_hop_num_per_articulation_point(self, overlay_topology: OverlayTopology, articulation_node: int) -> Dict[str, int]:
    '''
    指定した関節点に対する最短経路を求める

    :params overlay_topology: OverlayTopology 対象のオーバーレイトポロジー
    :params articulation_node: int 関節点のノード番号(オーバーレイネットワーク上の番号)
    :return shortest_hop_num: Dict[str, int] 指定した関節点を削除するための親ノード，子ノード，そのホップ数（ノード番号は物理ネットワーク）
    '''
    child_node_list = []
    # 関節点が持つ全ての子ノードをリストに格納
    node_num = len(overlay_topology.adj_matrix)
    for adj_node in range(node_num):
      if overlay_topology.adj_matrix[articulation_node][adj_node] == 1 \
        and overlay_topology.dfs_tree.search_order[articulation_node] < overlay_topology.dfs_tree.search_order[adj_node]:
        child_node_list.append(adj_node)

    # 関節点の子ノードから親ノードに対する最短経路のdictを入れたリスト
    # shortest_path_per_child[int]['parent'] -> 親ノードのノード番号
    # shortest_path_per_child[int]['hop_num'] -> 最短経路のホップ数 
    shortest_path_per_child = [{} for _ in range(len(child_node_list))]
    # print(shortest_path_per_child)
    # print('parent: ', overlay_topology.dfs_tree.parent)

    for child_node in range(len(child_node_list)):
      # 子ノードをオーバーレイネットワークの番号から物理ネットワークの番号へ変換
      node_num_of_child = child_node_list[child_node]
      child_node_on_substrate = overlay_topology.node_list_mapping_to_substrate[node_num_of_child]

      # 各ノードの親ノードが格納されたリスト
      overlay_node_parents = overlay_topology.dfs_tree.parent

      # 親ノードと先祖ノード（親ノードの親）をリストに格納
      ancestor_nodes = []
      tmp_node = articulation_node
      
      while True:
        if overlay_node_parents[tmp_node] == -1:
          break
        tmp_node = overlay_node_parents[tmp_node]
        ancestor_nodes.append(tmp_node)
      
      # print('anc_list', ancestor_nodes)
      # child_nodeがDFS Treeの根ノードであれば次のノードへ
      if len(ancestor_nodes) == 0:
        continue

      hop_num_list_from_child_to_parents = [None] * len(ancestor_nodes)
      
      # 距離行列の作成
      adj_csr_matrix = csr_matrix(overlay_topology.substrate_adj_matrix_without_overlay)

      dist_matrix, predecessors = dijkstra(csgraph=adj_csr_matrix, directed=False, return_predecessors=True)
      dist_matrix = dist_matrix.astype(int)

      # 全ての親ノードに対して，子ノードからの最短パスを求める
      for parent_node in range(len(ancestor_nodes)):
        parent_node_on_substrate = overlay_topology.node_list_mapping_to_substrate[ancestor_nodes[parent_node]]
        # print(parent_node_on_substrate)
        if dist_matrix[child_node_on_substrate][parent_node_on_substrate] > 0:
          hop_num_list_from_child_to_parents[parent_node] = dist_matrix[child_node_on_substrate][parent_node_on_substrate]
        else:
          hop_num_list_from_child_to_parents[parent_node] = 100
    
      # print('hop num list ', hop_num_list_from_child_to_parents)
      # 子ノードに対して最短パスを持つ親ノードの番号を取得
      min_hop_parent_index = hop_num_list_from_child_to_parents.index(min(hop_num_list_from_child_to_parents))
      min_hop_parent = ancestor_nodes[min_hop_parent_index]

      shortest_path_per_child[child_node]['parent'] = min_hop_parent
      shortest_path_per_child[child_node]['hop_num'] = min(hop_num_list_from_child_to_parents)
    # print(shortest_path_per_child)

    shortest_path = {'parent': None, 'child': None, 'hop_num': 10000}
    for i in range(len(shortest_path_per_child)):
      if shortest_path_per_child[i]['hop_num'] < shortest_path['hop_num']:
        shortest_path['hop_num'] = shortest_path_per_child[i]['hop_num']

        shortest_path_parent = shortest_path_per_child[i]['parent']
        shortest_path['parent'] = overlay_topology.node_list_mapping_to_substrate[shortest_path_parent]

        shortest_path_child = child_node_list[i]
        shortest_path['child'] = overlay_topology.node_list_mapping_to_substrate[shortest_path_child]
    # print(shortest_path)
    return shortest_path


  def _extend_overlay_topology(self, overlay_topology: OverlayTopology, topology_manager: TopologyManager, parent: int, child: int) -> None:
    '''
    指定したノード間の最短経路上のノードをオーバーレイトポロジーに追加する

    '''
    add_node_list = []
    # 物理ネットワーク上のオーバーレイトポロジーで使用されていない資源から距離行列を作成
    adj_csr_matrix = csr_matrix(overlay_topology.substrate_adj_matrix_without_overlay)
    dist_matrix, predecessors = dijkstra(csgraph=adj_csr_matrix, directed=False, return_predecessors=True)
    dist_matrix = dist_matrix.astype(int)

    # print("src = " + str(child_node_on_sub) + " , dst = " + str(parent) + " path is")
    dst = parent
    for i in range(dist_matrix[child][parent]):
      # print(predecessors[child][dst])
      add_node_list.append(predecessors[child][dst])
      dst = predecessors[child][dst]     


    ovrelay_nodes = overlay_topology.node_list_mapping_to_substrate
    ovrelay_nodes.extend(add_node_list)
    ovrelay_nodes = list(set(ovrelay_nodes))


    slice_adj_matrix = topology_manager.extract_slice_from_substrate_topo(overlay_topology.substrate_adj_matrix, ovrelay_nodes)
    overlay_topology.adj_matrix = slice_adj_matrix
    overlay_topology.node_list_mapping_to_substrate = ovrelay_nodes

    overlay_topology.update_attribute()



  def _get_parent_child_pair(self, overlay_topology: OverlayTopology, articulation_points_list: List[int]) -> Dict[str, int]:
    '''
    全ての関節点に対して，その親要素から子要素への経路を計算し，最短経路をもつ関節点を出力する
    :return shortest_path: Dict[str, int] 全ての子ノード，親ノードのペアのなかで最もホップ数の少ない経路
    '''
    # print('parent in _ger_parent_child: ', overlay_topology.dfs_tree.parent)
    # print('0 個数: ', overlay_topology.substrate_adj_matrix_without_overlay[1].count(0))
    articulation_point_num = len(articulation_points_list)

    shortest_path = [None] * articulation_point_num

    min_hop_num = 100
    for i in range(articulation_point_num):
      shortest_path[i] = self._get_hop_num_per_articulation_point(overlay_topology, articulation_points_list[i])
      # print('shortest_path per arcp', shortest_path[i])
      if shortest_path[i]['hop_num'] < min_hop_num:
        min_hop_index = i
        min_hop_num = shortest_path[i]['hop_num']
    
    if min_hop_num == 100:
      return None

    # print('shortest_path', shortest_path[min_hop_index])
    
    parent_child_pair = {'parent': shortest_path[min_hop_index]['parent'], 
                        'child': shortest_path[min_hop_index]['child']}

    return parent_child_pair


  def create_biconnect_graph(self, overlay_topology: OverlayTopology, topology_manager: TopologyManager) -> None:
    '''
    二重連結のオーバーレイトポロジーを作成する
    
    '''

    start_point = 0
    while True:
      # 関節点の検出
      articulation_points_list = topology_manager.find_articulation_points(overlay_topology)
      # print('articulation list', articulation_points_list)

      if len(articulation_points_list) == 0:
        # 構成数4でMRCを実行する場合に不具合が発生するケースを除いてbreak（TODO 構成数の拡張性）
        # この時点でMRC対象のオーバーレイネットワークが完成
        if len(overlay_topology.adj_matrix) < 4 or overlay_topology.is_degree_greater_than_2():
          break
        
        else:
          self.connect_overlay_topology(overlay_topology, topology_manager, reconnect=True)
          # overlay_topology.adj_list = overlay_topology.to_adj_list_from_matrix(overlay_topology.overlay_topology)
          continue

      # DFSの始点を変更(関節点から探索を始めてしまうと，都合が悪いため)      
      while start_point in articulation_points_list:
        start_point += 1
      # print('start point', start_point)
      # print('parent before search: ', overlay_topology.dfs_tree.parent)
      articulation_points_list = topology_manager.find_articulation_points(overlay_topology, start_point)
      # print('parent after search: ', overlay_topology.dfs_tree.parent)
      
      # 全ての関節点に対して，それを削除できる経路が物理ネットワークに存在しなかった場合
      # 探索の始点を変えて再トライ（オーバーレイネットワークのノード番号を変える）
      # print('overlay list ', overlay_topology.node_list_mapping_to_substrate)
      parent_child_pair = self._get_parent_child_pair(overlay_topology, articulation_points_list)
      if parent_child_pair is None:
        start_point += 1
        continue

      self._extend_overlay_topology(overlay_topology, topology_manager, parent_child_pair['parent'], parent_child_pair['child'])
      # print('node added')
      # print(overlay_topology.node_list_mapping_to_substrate)
      # print()


    return None
    
