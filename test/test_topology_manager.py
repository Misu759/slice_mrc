import unittest

import my_module
from overlay_topology import OverlayTopology
from topology_changer import TopologyChanger
from topology_manager import TopologyManager
import path_strings_collection as path_str


substrate_adj_matrix = my_module.from_file_to_adj_matrix(path_str.substrate_topo_file)
# TODO rand_ints_nodup()の引数→len(sub_adj)とスライスノード数に変更する
# slice_node = my_module.rand_ints_nodup(0, len(substrate_adj_matrix) - 1, SLICE_NODE_NUM)


topo_man = TopologyManager()
topo_changer = TopologyChanger()

class TopologyManagerTestCase(unittest.TestCase):
  def test_class_valid(self):
    self.assertIsInstance(topo_man, TopologyManager)
  
  def test_extract_slice(self):
    slice_node = [0, 1, 3]
    slice_adj_matrix = topo_man.extract_slice_from_substrate_topo(substrate_adj_matrix, slice_node)
    self.assertEqual(len(slice_adj_matrix), 3)
    self.assertEqual(slice_adj_matrix[0][0], 0)
    self.assertEqual(slice_adj_matrix[0][1], 1)

  def test_extract_slice2(self):
    slice_node = [0, 2, 5]
    slice_adj_matrix = topo_man.extract_slice_from_substrate_topo(substrate_adj_matrix, slice_node)
    self.assertEqual(len(slice_adj_matrix), 3)
    self.assertEqual(slice_adj_matrix[0][0], 0)
    self.assertEqual(slice_adj_matrix[0][1], 0)

  def test_extract_slice3(self):
    slice_node = [6, 10, 16]
    slice_adj_matrix = topo_man.extract_slice_from_substrate_topo(substrate_adj_matrix, slice_node)
    self.assertEqual(len(slice_adj_matrix), 3)
    self.assertEqual(slice_adj_matrix[0][0], 0)
    self.assertEqual(slice_adj_matrix[0][1], 0)
    self.assertEqual(slice_adj_matrix[1][2], 1)


  def test_generate_overlay(self):
    slice_node = [6, 10, 16]
    overlay_topology = topo_man.generate_overlay_network(substrate_adj_matrix, slice_node)

    self.assertIsInstance(overlay_topology, OverlayTopology)
    self.assertEqual(len(overlay_topology.adj_matrix), 3)
    self.assertEqual(overlay_topology.adj_matrix[0][0], 0)
    self.assertEqual(overlay_topology.adj_matrix[0][1], 0)
    self.assertEqual(overlay_topology.adj_matrix[1][2], 1)

    self.assertEqual(overlay_topology.node_list_mapping_to_substrate, [6, 10, 16]) 

    topo_changer.connect_overlay_topology(overlay_topology, topo_man)
    self.assertEqual(overlay_topology.node_list_mapping_to_substrate, [6, 7, 10, 16])
    self.assertEqual(overlay_topology.adj_matrix[0][0], 0)
    self.assertEqual(overlay_topology.adj_matrix[1][1], 0)
    self.assertEqual(overlay_topology.adj_matrix[0][1], 1)
    self.assertEqual(overlay_topology.adj_matrix[1][3], 0)
    self.assertEqual(overlay_topology.adj_matrix[2][3], 1)

    # substrate_adj_mat_without_overlayがあっているか
    self.assertEqual(overlay_topology.substrate_adj_matrix_without_overlay[6][7], 0)
    self.assertEqual(overlay_topology.substrate_adj_matrix_without_overlay[6][8], 1)
    self.assertEqual(overlay_topology.substrate_adj_matrix_without_overlay[7][10], 0)
    self.assertEqual(overlay_topology.substrate_adj_matrix_without_overlay[7][9], 1)

    # adj_matrix_on_substrateがあっているか
    self.assertEqual(overlay_topology.adj_matrix_on_substrate[6][7], 1)
    self.assertEqual(overlay_topology.adj_matrix_on_substrate[6][8], 0)
    self.assertEqual(overlay_topology.adj_matrix_on_substrate[7][10], 1)
    self.assertEqual(overlay_topology.adj_matrix_on_substrate[7][9], 0)
    self.assertEqual(overlay_topology.adj_matrix_on_substrate[10][16], 1)


  def test_generate_overlay2(self):
    slice_node = [0, 5, 7]
    overlay_topology = topo_man.generate_overlay_network(substrate_adj_matrix, slice_node)

    self.assertIsInstance(overlay_topology, OverlayTopology)
    self.assertEqual(len(overlay_topology.adj_matrix), 3)
    self.assertEqual(overlay_topology.adj_matrix[0][0], 0)
    self.assertEqual(overlay_topology.adj_matrix[0][1], 0)
    self.assertEqual(overlay_topology.adj_matrix[1][2], 0)

    self.assertEqual(overlay_topology.node_list_mapping_to_substrate, [0, 5, 7]) 

    topo_changer.connect_overlay_topology(overlay_topology, topo_man)
    self.assertEqual(overlay_topology.node_list_mapping_to_substrate, [0, 3, 5, 7])
    self.assertEqual(overlay_topology.adj_matrix[0][0], 0)
    self.assertEqual(overlay_topology.adj_matrix[1][1], 0)
    self.assertEqual(overlay_topology.adj_matrix[0][1], 1)
    self.assertEqual(overlay_topology.adj_matrix[1][3], 1)
    self.assertEqual(overlay_topology.adj_matrix[2][3], 0)

    # substrate_adj_mat_without_overlayがあっているか
    self.assertEqual(overlay_topology.substrate_adj_matrix_without_overlay[0][3], 0)
    self.assertEqual(overlay_topology.substrate_adj_matrix_without_overlay[0][1], 1)
    self.assertEqual(overlay_topology.substrate_adj_matrix_without_overlay[3][5], 0)
    self.assertEqual(overlay_topology.substrate_adj_matrix_without_overlay[7][10], 1)

    # adj_matrix_on_substrateがあっているか
    self.assertEqual(overlay_topology.adj_matrix_on_substrate[0][3], 1)
    self.assertEqual(overlay_topology.adj_matrix_on_substrate[3][5], 1)
    self.assertEqual(overlay_topology.adj_matrix_on_substrate[2][3], 0)
    self.assertEqual(overlay_topology.adj_matrix_on_substrate[7][10], 0)
    self.assertEqual(overlay_topology.adj_matrix_on_substrate[10][16], 0)
