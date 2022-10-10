from typing import List
import copy

class NormalConfiguration(object):
  def __init__(self, adj_matrix: List[int]) -> None:
    self.node_num = len(adj_matrix)
    self.adj_matrix = copy.deepcopy(adj_matrix)
    self.link_num = self._get_link_num()
  
  def _get_link_num(self) -> int:
    link_num = 0
    for i in range(self.node_num):
      for j in range(self.node_num):
        if self.adj_matrix[i][j] == 1:
          link_num += 1
    
    return link_num

