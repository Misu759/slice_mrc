import sys
import random
import copy
import yaml

from constants import BACKUP_CONF_NUM, NUM_OF_SLICES, SLICE_NODE_NUM, SLICE_NUM_PER_ATTEMPT
import my_module
from topology_manager import TopologyManager
from topology_changer import TopologyChanger
import path_strings_collection as path_str


random.seed(1)

def main(argv):
  substrate_adj_matrix = my_module.from_file_to_adj_matrix(path_str.substrate_topo_file)

  topology_manager = TopologyManager()
  topology_changer = TopologyChanger()

  for slice_count in range(NUM_OF_SLICES):
    slice_nodes = my_module.rand_ints_nodup(0, len(substrate_adj_matrix)-1, SLICE_NODE_NUM)

    overlay_topology = topology_manager.generate_overlay_network(substrate_adj_matrix, slice_nodes)
    topology_changer.connect_overlay_topology(overlay_topology, topology_manager)

    topology_changer.create_biconnect_graph(overlay_topology, topology_manager)

    while len(overlay_topology.adj_matrix) <= len(substrate_adj_matrix):
      start_point = 0
      while start_point < overlay_topology.node_num:
        mrc = topology_manager.apply_mrc(overlay_topology.adj_matrix, 'check_mrc/output'+str(slice_count)+'/backup', start_point)
        if not mrc:
          start_point += 1
        else:
          print('スライス', slice_count, 'のMRCが正常に実行されました')
          
          # TODO このタイミングでバックアップ構成のデータをyaml書き出し  
          biconnected_graph_nodes = []
          for i in overlay_topology.node_list_mapping_to_substrate:
            biconnected_graph_nodes.append(int(i))
          
          backup_configurations_list = []
          isolated_nodes_list = []

          for i in range(BACKUP_CONF_NUM):
            backup_configurations_list.append(mrc.backup_conf[i].adj_matrix)
            isolated_nodes_list.append(mrc.backup_conf[i].isolated_nodes_set)
          slice_backup_configuration_data = {
            'slice_nodes': slice_nodes,
            # これだけなぜか文字列に変換しないとバグが起きる(ログとして残すだけなので一旦はこのままで)
            'biconnected_graph_nodes': biconnected_graph_nodes,
            'backup_configurations': backup_configurations_list,
            'isolated_nodes': isolated_nodes_list
          }

          with open('yaml/slice' + str(slice_count) + '_mrc_result.yaml', 'w') as f:
            yaml.dump(slice_backup_configuration_data, f, default_flow_style=False, allow_unicode=True)
          
          break
      # あってるかわからない
      # [TODO] 結果の取り方決めてから実行してみる
      else:
        topology_changer.connect_overlay_topology(overlay_topology, topology_manager, reconnect=True)
        topology_changer.create_biconnect_graph(overlay_topology, topology_manager)
        continue
      
      break



if __name__ == '__main__':
  sys.exit(main(sys.argv))