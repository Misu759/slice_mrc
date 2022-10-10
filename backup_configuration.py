import copy
import queue
from typing import List
from scipy.sparse.csgraph import dijkstra

from normal_configuration import NormalConfiguration

# 制限リンクの重み
RESTRICT_WEIGHT = 1000
# 分離リンクの重み
ISOLATE_WEIGHT = 100000

class BackupConfiguration(NormalConfiguration):
  def __init__(self, adj_matrix) -> None:
    super().__init__(adj_matrix)
    self.isolated_nodes_set = set()
    self.normal_nodes_matrix = copy.deepcopy(adj_matrix)
    self.normal_nodes_list = []

    self.connected_links_queue = queue.Queue()
    self.links_queue_for_sorting = queue.Queue()
  

  def can_isolate_a_node(self, copied_normal_nodes_matrix: List[int], isolating_node: int) -> bool:
    '''
    指定したノードを除いた時に他の全てのノードが接続されているか判別

    あるバックアップ構成において，ノードを分離するには，そのノードを除いた全てのノード間が接続している必要がある
    :params isolating_node int: 分離しようとしているノードの番号
    :return connect_flag bool: 接続しているか 
    '''
    for node_i in range(self.node_num):
      if node_i == isolating_node or node_i in self.isolated_nodes_set:
        continue
      for node_j in range(self.node_num):
        if node_i == node_j or node_j == isolating_node or node_j in self.isolated_nodes_set:
          continue
        elif 0 < dijkstra(copied_normal_nodes_matrix)[node_i][node_j] < 100:
          connect_flag = True
        else:
          connect_flag = False
          break
    
    return connect_flag
  
  def can_isolate_a_link(self, isolationg_node: int, connected_node: int) -> bool:
    '''
    指定した２つのノード間のリンクが分離可能か判定

    分離ノードは少なくとも一つの制限リンクと接続されていなければならない
    '''
    for i in range(self.node_num):
      if i != connected_node \
        and (self.adj_matrix[isolationg_node][i] == RESTRICT_WEIGHT \
            or self.adj_matrix[isolationg_node][i] == 1):

        return True
    
    return False

  
  def set_isolate_weight(self, isolating_node: int, connected_node: int) -> None:
    self.adj_matrix[isolating_node][connected_node] = ISOLATE_WEIGHT
    self.adj_matrix[connected_node][isolating_node] = ISOLATE_WEIGHT
  
  def set_restrict_weight(self, isolating_node: int, connected_node: int) -> None:
    self.adj_matrix[isolating_node][connected_node] = RESTRICT_WEIGHT
    self.adj_matrix[connected_node][isolating_node] = RESTRICT_WEIGHT