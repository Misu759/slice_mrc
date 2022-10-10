import unittest
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra

from constants import BACKUP_CONF_NUM
import my_module
import path_strings_collection as path_str
from multiple_routing_configurations import MultipleRoutingConfigurations
from topology_manager import TopologyManager
from result_calculator import ResultCalculator


# 制限リンクの重み
RESTRICT_WEIGHT = 1000
# 分離リンクの重み
ISOLATE_WEIGHT = 100000

adj_matrix = my_module.from_file_to_adj_matrix(path_str.substrate_topo_file)
topology_manager = TopologyManager()

class MultipleRoutingConfigurationsTestCase(unittest.TestCase):
  def test_class_valid(self):
    mrc = MultipleRoutingConfigurations(adj_matrix)
    # 正常にインスタンスを作成できているか
    self.assertIsInstance(mrc, MultipleRoutingConfigurations)
    # 通常構成のトポロジーの大きさが対象のトポロジーと一致しているか
    self.assertEqual(len(mrc.normal_conf.adj_matrix), len(adj_matrix))
    # 指定した数のバックアップルーティング構成を作成できているか
    self.assertEqual(len(mrc.backup_conf), BACKUP_CONF_NUM)
    # バックアップルーティング構成のトポロジーの大きさが対象のトポロジーと一致しているか
    self.assertEqual(len(mrc.backup_conf[0].adj_matrix), len(adj_matrix))

  def test_apply_mrc(self):
    mrc = topology_manager.apply_mrc(mrc_subject_adj_matrix=adj_matrix,
                                         output_file_name='check_mrc/output', 
                                         start_point=13)
    self.assertTrue(mrc)

    # 全てのノードがどれか一つの構成で分離されている
    is_all_node_isolated = True
    node_num = len(adj_matrix)
    for node in range(node_num):
      for conf_num in range(BACKUP_CONF_NUM):
        if node in mrc.backup_conf[conf_num].isolated_nodes_set:
          break
      else:
        is_all_node_isolated = False
        print('node', node, 'is not isolated.')

    self.assertTrue(is_all_node_isolated)

    # 全てのリンクはどれか一つの構成で分離されている
    is_all_link_isolated = True
    for i in range(node_num):
      for j in range(i+1, node_num):
        # 全てのリンク(i, j)に対して
        if adj_matrix[i][j] == 1:
          for conf_num in range(BACKUP_CONF_NUM):
            if mrc.backup_conf[conf_num].adj_matrix[i][j] == ISOLATE_WEIGHT:
              # 隣接行列が正しくできているかどうか
              self.assertEqual(mrc.backup_conf[conf_num].adj_matrix[j][i], ISOLATE_WEIGHT)
              break
          else:
            is_all_link_isolated = False
            print('分離できていないリンクがあります')
    
    self.assertTrue(is_all_link_isolated)

    # バックアップルーティング構成は分離ノードを除いた全てのノード間が通常リンクによって，接続されている
    is_normal_topology_connected = True
    for conf_num in range(BACKUP_CONF_NUM):
      normal_csr_adj_matrix = csr_matrix(mrc.backup_conf[conf_num].normal_nodes_matrix)
      normal_dist_martix = dijkstra(csgraph=normal_csr_adj_matrix, directed=False, return_predecessors=False).astype(int)

      for i in range(node_num):
        if i not in mrc.backup_conf[conf_num].isolated_nodes_set:
          for j in range(node_num):
            if j not in mrc.backup_conf[conf_num].isolated_nodes_set \
                and normal_dist_martix[i][j] < 0:
              is_normal_topology_connected = False
              print('バックアップ構成' + str(conf_num) + 'において，通常ノード同士が連結していないです')
  
    self.assertTrue(is_normal_topology_connected)

    # 分離ノードには分離リンク，または制限リンクが接続され，通常リンクは接続されない
    is_not_connected_normal_link_to_isolated_node = True
    for conf_num in range(BACKUP_CONF_NUM):
      for isolate_node in mrc.backup_conf[conf_num].isolated_nodes_set:
        for node in range(node_num):
          if mrc.backup_conf[conf_num].adj_matrix[isolate_node][node] != 0 \
              and mrc.backup_conf[conf_num].adj_matrix[isolate_node][node] != RESTRICT_WEIGHT \
                and mrc.backup_conf[conf_num].adj_matrix[isolate_node][node] != ISOLATE_WEIGHT:
            print('バックアップ構成', conf_num, 'の分離ノードに通常リンクが接続されている，または隣接行列に正常でない値が入っています')
            is_not_connected_normal_link_to_isolated_node = False
    
    self.assertTrue(is_not_connected_normal_link_to_isolated_node)


    # 分離リンクには，少なくとも一つの制限リンクが接続されている
    is_connected_restricted_link_to_isolated_node = True
    for conf_num in range(BACKUP_CONF_NUM):
      for isolate_node in mrc.backup_conf[conf_num].isolated_nodes_set:
        for node in range(node_num):
          if mrc.backup_conf[conf_num].adj_matrix[isolate_node][node] != RESTRICT_WEIGHT:
            break
        else:
          print('バックアップ構成', conf_num, 'の分離ノード', node, 'に制限リンクが接続されていません')
          is_connected_restricted_link_to_isolated_node = False
    
    self.assertTrue(is_connected_restricted_link_to_isolated_node)