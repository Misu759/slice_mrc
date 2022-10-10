import unittest
import yaml

from result_calculator import ResultCalculator
from constants import BACKUP_CONF_NUM

result_calculator = ResultCalculator()

class TopologyManagerTestCase(unittest.TestCase):
  def test_class_valid(self):
    self.assertIsInstance(result_calculator, ResultCalculator)
  
  def test_calculate_hop_num_per_conf(self):
    backup_conf_adj_matrix = [None] * BACKUP_CONF_NUM
    for conf in range(BACKUP_CONF_NUM):
      with open('yaml/slice0_mrc_result.yaml', encoding='utf-8') as f:
        slice_data = yaml.safe_load(f)
      
      backup_conf_adj_matrix[conf] = slice_data['backup_configurations'][conf]
      # TODO ハードコードの修正
      hop_num_list = result_calculator._calculate_backup_hops_per_conf(backup_conf_adj_matrix[conf], slice_data['slice_nodes'])
      self.assertEqual(len(hop_num_list), 3)
      self.assertTrue(all(hop_num_list) > 0)
  
  # 作成したバックアップ構成のホップ数と，その最大値を求める処理
  def test_mrc_calculate_hop_num(self):
    backup_conf_adj_matrix = [None] * BACKUP_CONF_NUM
    with open('yaml/slice3_mrc_result.yaml', encoding='utf-8') as f:
      slice_data = yaml.safe_load(f)
    for conf in range(BACKUP_CONF_NUM):
      backup_conf_adj_matrix[conf] = slice_data['backup_configurations'][conf]

    result_calculator.output_hop_count_yaml(slice_count=3, backup_configurations=backup_conf_adj_matrix)
    
    # 出力先を確認
    for conf in range(BACKUP_CONF_NUM):
      with open('yaml/slice3_mrc_result.yaml', encoding='utf-8') as f:
        slice_data = yaml.safe_load(f)
    
    self.assertEqual(len(slice_data['hop_num_raw_data']), 12)
  

  def test_get_backup_path(self):
    result = result_calculator.get_backup_path(slice_count=2)
    print(result)
    self.assertEqual(len(result), BACKUP_CONF_NUM)
  
  def test_get_backup_path_in_substrate_mrc(self):
    result = result_calculator.get_backup_path(slice_count=2, is_overlay_mrc=False)
    print(result)
    self.assertEqual(len(result), BACKUP_CONF_NUM)

  def test_get_normal_path(self):
    without_failure_path_list = result_calculator.get_normal_path(slice_count=2)
    # print(without_failure_path_list)
    self.assertEqual(len(without_failure_path_list), 3)