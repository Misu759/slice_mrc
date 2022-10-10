from typing import List
import sys
import yaml

from constants import BACKUP_CONF_NUM, RESTRICT_WEIGHT
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
import my_module
import path_strings_collection as path_str

class ResultCalculator(object):
  def __init__(self) -> None:
    pass

  def _calculate_backup_hops_per_conf(self, backup_adj_matrix: List[int], node_list: List[int]) -> List[int]:
    '''
    与えらえたバックアップ構成に対してホップ数の計算を行う

    引数として渡すリストに格納されたノードの組み合わせに対して，指定したバックアップルーティング構成における経路を計算する
    :params backup_adj_martix: List[int] バックアップルーティング構成の隣接行列
    :params node_list: List[int] 経路を計算したいノードのリスト（オーバーレイトポロジーのノード番号を指定），
    :return hop_num_list: List[int] 任意のノード間のホップ数（生データ）が格納されたリスト
    '''
    # ホップ数を計測するノードを昇順に並び替える
    node_list.sort()
    # バックアップルーティング構成の距離行列を取得
    backup_adj_matrix = csr_matrix(backup_adj_matrix)
    dist_matrix = dijkstra(csgraph=backup_adj_matrix, directed=False)

    # それぞれのノードの組み合わせに対するホップ数を取得し，リストに格納
    hop_num_list = []
    for src_node in node_list:
      src_node_index = node_list.index(src_node)
      for dst_node in node_list[src_node_index + 1 :]:
        hop_num = self._remove_backup_configuration_weight(dist_matrix[src_node][dst_node])
        hop_num_list.append(hop_num)
    
    return hop_num_list
  

  def output_hop_count_yaml(self, slice_count: int, backup_configurations: List[int]) -> None:
    '''
    経路のホップ数を取得して, yaml出力する

    :params slice_count: int ホップ数を取得したいスライスの番号
    :params backup_configurations: List[int] バックアップ構成の隣接行列（全ての構成を格納したリスト）
    '''
    with open('yaml/slice' + str(slice_count) + '_mrc_result.yaml', encoding='utf-8') as f:
      data = yaml.safe_load(f)
    
    slice_nodes = data['slice_nodes']
    biconnected_graph_nodes = data['biconnected_graph_nodes']

    slice_node_index = []
    for i in range(len(biconnected_graph_nodes)):
      if biconnected_graph_nodes[i] in slice_nodes:
        slice_node_index.append(i)

    hop_num_data = []
    for i in range(BACKUP_CONF_NUM):
      hop_num_per_conf = self._calculate_backup_hops_per_conf(backup_configurations[i], slice_node_index)
      hop_num_data.extend(hop_num_per_conf)
    
    # yaml出力用にint型に変換（numpy配列のデータはそのまま出力するとバグるので）
    hop_num_int_data = []
    for i in hop_num_data:
      hop_num_int_data.append(int(i))

    add_yaml_data = {'hop_num_raw_data': hop_num_int_data}

    with open('yaml/slice' + str(slice_count) + '_mrc_result.yaml', 'a') as f:
      yaml.dump(add_yaml_data, f, default_flow_style=False, allow_unicode=True)

  

  def get_backup_path(self, slice_count: int, is_overlay_mrc: bool = True) -> List[int]:
    '''
    スライスのバックアップ構成における経路上のノード番号を取得する

    :params slice_count: int 経路を取得したいスライスの番号を指定
    :params is_overlay_mrc: bool オーバーレイグラフに対して作成したバックアップ構成における経路を取得するかどうか
    物理ネットワーク全体に対して作成したバックアップ構成の経路を求める場合は, Falseにする
    :return backup_path_list: List[Dict[int]] 全てのバックアップルーティング構成におけるスライスの経路
    リストの要素数 = バックアップ構成数で，各要素は経路上のノード番号を，送信元/宛先ノードの組み合わせ（タプル）をキーとした辞書型で格納
    '''
    with open('yaml/slice' + str(slice_count) + '_mrc_result.yaml', encoding='utf-8') as f:
      data = yaml.safe_load(f)
    
    slice_nodes = data['slice_nodes']
    slice_nodes.sort()

    if is_overlay_mrc:
      # 物理ネットワークのノード番号をオーバーレイネットワークに対して
      # 作成したグラフのノード番号に変換する
      tmp_slice_nodes = []
      biconnected_graph_nodes = data['biconnected_graph_nodes']

      loop_start = 0
      for slice_node in slice_nodes:
        for i in range(loop_start, len(biconnected_graph_nodes)):
          if biconnected_graph_nodes[i] == slice_node:
            tmp_slice_nodes.append(i)
            loop_start = i + 1
      
      slice_nodes = tmp_slice_nodes

    else:
      # 物理ネットワーク全体に対して作成したバックアップルーティング構成のデータを取得
      with open('German_topo/substrate_topology.yaml', encoding='utf-8') as f:
        data = yaml.safe_load(f)


    backup_path_list = [[] for _ in range(BACKUP_CONF_NUM)]

    for conf_i in range(BACKUP_CONF_NUM):
      backup_adj_matrix = data['backup_configurations'][conf_i]

      backup_adj_matrix = csr_matrix(backup_adj_matrix)
      dist_matrix, predecessors = dijkstra(csgraph=backup_adj_matrix, directed=False, return_predecessors=True)

      for src_node in slice_nodes:
        src_node_index = slice_nodes.index(src_node)
        for dst_node in slice_nodes[src_node_index + 1 :]:
          # バックアップルーティング構成の距離行列から2点間の値を取得し，重みを取り除く → ホップ数
          hop_num_with_weight = dist_matrix[src_node][dst_node]
          hop_num = self._remove_backup_configuration_weight(hop_num_with_weight)

          tmp_path_list = self._get_path_list(src_node, dst_node, int(hop_num), predecessors)

          # 経路のリストには物理ネットワークのノード番号を格納する
          if is_overlay_mrc:
            tmp_path_list = self._to_substrate_index(tmp_path_list, biconnected_graph_nodes)
            backup_path_list[conf_i].append({(biconnected_graph_nodes[src_node], biconnected_graph_nodes[dst_node]): tmp_path_list})
          else:
            backup_path_list[conf_i].append({(src_node, dst_node): tmp_path_list})

    return backup_path_list


  def get_normal_path(self, slice_count: int) -> List[int]:
    '''
    物理ネットワークにおける最短経路上のノード番号を取得する

    経路上に障害が発生していない場合に使用（物理ネットワークに対する通常ルーティング構成）
    指定したスライスのノード間の経路を返す
    :params slice_count: int 経路を取得したスライスの番号
    :return shortest_path_list: List[int] 物理ネットワークでの最短経路上のノード番号
    '''
    substrate_adj_matrix = my_module.from_file_to_adj_matrix(path_str.substrate_topo_file)
    with open('yaml/slice' + str(slice_count) + '_mrc_result.yaml', encoding='utf-8') as f:
      data = yaml.safe_load(f)
    
    slice_nodes = data['slice_nodes']
    slice_nodes.sort()

    shortest_path_list = []

    substrate_adj_matrix = csr_matrix(substrate_adj_matrix)
    dist_matrix, predecessors = dijkstra(csgraph=substrate_adj_matrix, directed=False, return_predecessors=True)

    for src_node in slice_nodes:
      src_node_index = slice_nodes.index(src_node)
      for dst_node in slice_nodes[src_node_index + 1 :]:
        tmp_path_list = self._get_path_list(src_node, dst_node, int(dist_matrix[src_node][dst_node]), predecessors)
        shortest_path_list.append({(src_node, dst_node): tmp_path_list})

    return shortest_path_list

  def _get_path_list(self, src_node: int, dst_node: int, hop_num: int, predecessors: List[int]):
    '''
    経路上のノードをリストに格納する

    :params src_node: int 取得したい経路の送信元ノードの番号
    :params dst_node: int 取得したい経路の宛先ノードの番号
    :params hop_num: int 経路のホップ数
    :params predecessor: List[int] 各ノードペアに対する最短経路のラストホップノードの番号が格納されたリスト
    '''
    tmp_path_list = []
    tmp_dst = dst_node

    # 経路上のノードをリストに格納(逆順に格納される)
    for _ in range(hop_num):
      tmp_path_list.append(tmp_dst)
      tmp_dst = predecessors[src_node][tmp_dst]
    
    # 最後に送信元をappendして，
    # 順番を入れ替えることで経路のノード番号を取得
    tmp_path_list.append(src_node)
    tmp_path_list.reverse()

    return tmp_path_list
  

  def _to_substrate_index(self, nodes_index_in_overlay, biconnected_graph_nodes):
    '''
    オーバーレイネットワークのノード番号から物理ネットワークのノード番号へ変換する
    '''
    substrate_index_list = []
    for node in nodes_index_in_overlay:
      substrate_index_list.append(biconnected_graph_nodes[node])
    return substrate_index_list
  

  def _remove_backup_configuration_weight(self, hop_number: int) -> int:
    '''
    ホップ数を計算するために，制限リンクにかけている重みを取り除く
    '''
    if hop_number >= 3 * RESTRICT_WEIGHT:
      print('バックアップ構成の経路に不具合があります')
      sys.exit()
    elif hop_number >= 2 * RESTRICT_WEIGHT:
      hop_number = hop_number - 2 * RESTRICT_WEIGHT + 2
    elif hop_number >= RESTRICT_WEIGHT:
      hop_number = hop_number - RESTRICT_WEIGHT + 1
    
    return hop_number
