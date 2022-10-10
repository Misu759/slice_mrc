from constants import DIRECTORY_NAME, SLICE_NODE_NUM, NUM_OF_SLICES

substrate_topo_file = '/home/misugi/Documents/slice_mrc/' + DIRECTORY_NAME + '/substrate_topo.txt'
substrate_backup_topo_file = '/home/misugi/Documents/slice_mrc/' + DIRECTORY_NAME + '/backup_topo'
extract_topo_file = '/home/misugi/Documents/slice_mrc/' + DIRECTORY_NAME + '/logs/extract_topo.txt'
searchable_topo_file = '/home/misugi/Documents/slice_mrc/' + DIRECTORY_NAME + '/logs/searchable_topo.txt'
mrc_subject_topo_file = '/home/misugi/Documents/slice_mrc/' + DIRECTORY_NAME + '/logs/slice.txt'
mrc_subject_backup_topo_file = '/home/misugi/Documents/slice_mrc/' + DIRECTORY_NAME + '/logs/backup_topo'

slice_log_file = '/home/misugi/Documents/slice_mrc/' + DIRECTORY_NAME + '/logs/slice_hop_num_log.txt'
slice_path_log_file = '/home/misugi/Documents/slice_mrc/' + DIRECTORY_NAME + '/logs/slice_path_log.txt'
sub_log_file = '/home/misugi/Documents/slice_mrc/' + DIRECTORY_NAME + '/logs/substrate_hop_num_log.txt'
sub_path_log_file = '/home/misugi/Documents/slice_mrc/' + DIRECTORY_NAME + '/logs/substrate_path_log.txt'
process_log_file = '/home/misugi/Documents/slice_mrc/' + DIRECTORY_NAME + '/logs/' + str(SLICE_NODE_NUM) + 'nodes_' + str(NUM_OF_SLICES) + 'slices_log.txt'

isolate_nodes_set_file = '/home/misugi/Documents/slice_mrc/' + DIRECTORY_NAME + '/logs/isolate_nodes_set/conf'

slice_result_file = '/home/misugi/Documents/slice_mrc/' + DIRECTORY_NAME + '/results/slice_result.txt'
substrate_result_file = '/home/misugi/Documents/slice_mrc/' + DIRECTORY_NAME + '/results/sub_nw_slice_result.txt'

def slice_path_per_node_failure_log_file(slice, failure_node):
    return '/home/misugi/Documents/slice_mrc/' + DIRECTORY_NAME + '/logs/' + str(SLICE_NODE_NUM) + 'nodes/path/slice' + str(slice) + '_node' + str(failure_node) + '_failure_path.txt'

def substrate_path_per_node_failure_log_file(slice, failure_node):
    return '/home/misugi/Documents/slice_mrc/' + DIRECTORY_NAME + '/logs/' + str(SLICE_NODE_NUM) + 'nodes/path/sub_nw_slice' + str(slice) + '_node' + str(failure_node) + '_failure_path.txt'


