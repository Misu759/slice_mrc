import unittest

import my_module
from topology_manager import TopologyManager
from topology_changer import TopologyChanger
import path_strings_collection as path_str


substrate_adj_matrix = my_module.from_file_to_adj_matrix(path_str.substrate_topo_file)

topo_man = TopologyManager()
topo_changer = TopologyChanger()

class TopologyManagerTestCase(unittest.TestCase):
  def test_class_valid(self):
    self.assertIsInstance(topo_changer, TopologyChanger)

  def test_connect_overlay_topology_1(self):
    overlay_topology = topo_man.generate_overlay_network(substrate_adj_matrix, [6, 10, 16])
    topo_changer.connect_overlay_topology(overlay_topology, topo_man)
    self.assertEqual(overlay_topology.node_list_mapping_to_substrate, [6, 7, 10, 16])

  def test_connect_overlay_topology_2(self):
    overlay_topology = topo_man.generate_overlay_network(substrate_adj_matrix, [0, 5, 8])
    topo_changer.connect_overlay_topology(overlay_topology, topo_man)
    self.assertEqual(overlay_topology.node_list_mapping_to_substrate, [0, 3, 5, 7, 8])


  def test_get_hop_num_per_articulation_point(self):
    overlay_topology = topo_man.generate_overlay_network(substrate_adj_matrix, [6, 7, 10, 16])
    overlay_topology.dfs_tree.depth_first_search(0, overlay_topology.adj_list)

    result_dict = topo_changer._get_hop_num_per_articulation_point(overlay_topology, articulation_node=2)
    self.assertEqual(result_dict, {'parent': 7, 'child': 16, 'hop_num': 2})

  def test_get_hop_num_per_articulation_point_2(self):
    overlay_topology = topo_man.generate_overlay_network(substrate_adj_matrix, [3, 5, 10, 11])
    overlay_topology.dfs_tree.depth_first_search(0, overlay_topology.adj_list)

    result_dict = topo_changer._get_hop_num_per_articulation_point(overlay_topology, articulation_node=2)
    self.assertEqual(result_dict, {'parent': 3, 'child': 11, 'hop_num': 6})

  def test_get_hop_num_per_articulation_point_3(self):
    overlay_topology = topo_man.generate_overlay_network(substrate_adj_matrix, [0, 3, 5, 7, 8])
    overlay_topology.dfs_tree.depth_first_search(0, overlay_topology.adj_list)

    result_dict = topo_changer._get_hop_num_per_articulation_point(overlay_topology, articulation_node=1)
    self.assertEqual(result_dict, {'parent': 0, 'child': 7, 'hop_num': 2})
  
  def test_get_hop_num_per_articulation_point_4(self):
    overlay_topology = topo_man.generate_overlay_network(substrate_adj_matrix, [0, 3, 5, 7, 8])
    overlay_topology.dfs_tree.depth_first_search(0, overlay_topology.adj_list)

    result_dict = topo_changer._get_hop_num_per_articulation_point(overlay_topology, articulation_node=3)
    self.assertEqual(result_dict, {'parent': 0, 'child': 8, 'hop_num': 3})

  def test_get_parent_child_pair(self):
    overlay_topology = topo_man.generate_overlay_network(substrate_adj_matrix, [6, 7, 10, 16])
    overlay_topology.dfs_tree.depth_first_search(0, overlay_topology.adj_list)

    result_dict = topo_changer._get_parent_child_pair(overlay_topology, articulation_points_list=[1, 2])
    self.assertEqual(result_dict, {'parent': 7, 'child': 16})

  def test_get_parent_child_pair_2(self):
    overlay_topology = topo_man.generate_overlay_network(substrate_adj_matrix, [3, 5, 10, 11])
    overlay_topology.dfs_tree.depth_first_search(0, overlay_topology.adj_list)

    result_dict = topo_changer._get_parent_child_pair(overlay_topology, articulation_points_list=[1, 2])
    self.assertEqual(result_dict, {'parent': 3, 'child': 10})

  def test_get_parent_child_pair_3(self):
    overlay_topology = topo_man.generate_overlay_network(substrate_adj_matrix, [0, 5, 8])
    topo_changer.connect_overlay_topology(overlay_topology, topo_man)
    # self.assertEqual(overlay_topology.node_list_mapping_to_substrate, [0, 3, 5, 7, 8])

    result_dict = topo_changer._get_parent_child_pair(overlay_topology, articulation_points_list=[1, 3])
    self.assertEqual(result_dict, {'parent': 0, 'child': 7})


  def test_biconnect(self):
    overlay_topology = topo_man.generate_overlay_network(substrate_adj_matrix, [6, 10, 16])
    topo_changer.connect_overlay_topology(overlay_topology, topo_man)

    topo_changer.create_biconnect_graph(overlay_topology, topo_man)
    self.assertEqual(overlay_topology.node_list_mapping_to_substrate, [6, 7, 8, 9, 10, 16])


  def test_biconnect2(self):
    overlay_topology = topo_man.generate_overlay_network(substrate_adj_matrix, [0, 5, 8])
    topo_changer.connect_overlay_topology(overlay_topology, topo_man)

    topo_changer.create_biconnect_graph(overlay_topology, topo_man)
    self.assertEqual(overlay_topology.node_list_mapping_to_substrate, [0, 1, 3, 5, 6, 7, 8, 10])
  
  def test_biconnect3(self):
    overlay_topology = topo_man.generate_overlay_network(substrate_adj_matrix, [0, 4, 5, 6])
    topo_changer.connect_overlay_topology(overlay_topology, topo_man)

    topo_changer.create_biconnect_graph(overlay_topology, topo_man)
    self.assertEqual(overlay_topology.node_list_mapping_to_substrate, [0, 1, 2, 3, 4, 5, 6, 7, 10])

  # def test_get_hop_num_per_articulation_point_4(self):
  #   overlay_topology = topo_man.generate_overlay_network(substrate_adj_matrix, [0, 1, 3, 4, 5, 6])
  #   overlay_topology.dfs_tree.depth_first_search(0, overlay_topology.adj_list)

  #   result_dict = topo_changer._get_hop_num_per_articulation_point(overlay_topology, articulation_node=0)
  #   self.assertEqual(result_dict, {'parent': 3, 'child': 1, 'hop_num': 2})