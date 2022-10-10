from typing import List
import copy

from topology import Topology

class OverlayTopology(Topology):
  '''
  オーバーレイネットワーク　[TODO]詳しく書く
  '''
  
  node_list_mapping_to_substrate: List[int]
  substrate_adj_matrix: List[int]
  adj_matrix_on_substrate: List[int]
  substrate_adj_matrix_without_overlay: List[int]
  flag_to_exit_recursion: bool

  def __init__(self, overlay_adj_matrix: List[int], overlay_node_list: List[int], substrate_adj_matrix: List[int]):
    super().__init__(overlay_adj_matrix)

    self.node_list_mapping_to_substrate = overlay_node_list
    self.substrate_adj_matrix = substrate_adj_matrix
    self.adj_matrix_on_substrate = self.extract_overlay_topology_from_substrate()
    self.substrate_adj_matrix_without_overlay = self.find_resources_not_used_overlay()

    # self.flag_to_exit_recursion = 0
  
  def update_attribute(self) -> None:
    super().update_attribute()
    self.adj_matrix_on_substrate = self.extract_overlay_topology_from_substrate()
    self.substrate_adj_matrix_without_overlay = self.find_resources_not_used_overlay()

  
  def extract_overlay_topology_from_substrate(self) -> List[int]:
    '''
    return: List[int] 物理ネットワークの隣接行列からオーバーレイネットワークに対応した要素だけを抽出した隣接行列
    '''
    substrate_node_num = len(self.substrate_adj_matrix)

    adj_matrix_on_substrate = [[0 for i in range(substrate_node_num)] for j in range(substrate_node_num)]

    for i in range(substrate_node_num):
        for j in range(substrate_node_num):
            if i in self.node_list_mapping_to_substrate and j in self.node_list_mapping_to_substrate \
              and self.substrate_adj_matrix[i][j] == 1:
              adj_matrix_on_substrate[i][j] = 1
    
    return adj_matrix_on_substrate


  def find_resources_not_used_overlay(self) -> List[int]:
    substrate_topo_not_used_slice = copy.deepcopy(self.substrate_adj_matrix)

    overlay_node_num = len(self.adj_matrix)
    for i in range(overlay_node_num):
      for j in range(overlay_node_num):
        if self.substrate_adj_matrix[self.node_list_mapping_to_substrate[i]][self.node_list_mapping_to_substrate[j]] == 1:
          substrate_topo_not_used_slice[self.node_list_mapping_to_substrate[i]][self.node_list_mapping_to_substrate[j]] = 0
  
    return substrate_topo_not_used_slice
  

  # ノードを次数を確認（全てのノードの次数が２である場合、MRCがうまく動かないため）
  def is_degree_greater_than_2(self) -> bool:
    for node in range(len(self.adj_matrix)):
      degree = len(self.adj_list[node])
      if degree > 2:
        return True
    else:
      return False