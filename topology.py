import sys
from collections import defaultdict
import numpy as np

import depth_first_search_tree

class Topology(object):

    def __init__(self, adj_matrix):
        self.node_num = len(adj_matrix)
        self.adj_matrix = adj_matrix
        self.adj_list = self.to_adj_list_from_matrix()
        self.dfs_tree = depth_first_search_tree.DepthFirstSearchTree(self.node_num)

    def update_attribute(self):
        self.node_num = len(self.adj_matrix)
        self.adj_list = self.to_adj_list_from_matrix()
        self.dfs_tree = depth_first_search_tree.DepthFirstSearchTree(self.node_num)
        self.dfs_tree.depth_first_search(0, self.adj_list)

    def add_link(self, node_i, node_j):
        self.adj_list[node_i].append(node_j)
        self.adj_list[node_j].append(node_i)

    # [TODO] なにやってるのか
    def to_adj_matrix_from_list(self):
        new_adj_matrix = [[0 for i in range(self.node_num)] for j in range(self.node_num)]
        for i in range(len(self.adj_matrix)):
            for j in range(len(self.adj_list[i])):
                new_adj_matrix[i][self.adj_list[i][j]] = 1
        return new_adj_matrix

    def to_adj_list_from_matrix(self):
        adj_dict = defaultdict(list)
        for i in range(len(self.adj_matrix)):
            for j in range(i+1, len(self.adj_matrix)):
                if self.adj_matrix[i][j] == 1:
                    adj_dict[i].append(j)
                    adj_dict[j].append(i)

        return adj_dict
            

    def find_articulation_points(self, node_num, start_point=0):
        self.dfs_tree = depth_first_search_tree.DepthFirstSearchTree(node_num)
        self.dfs_tree.depth_first_search(start_point, self.adj_list)

        for i in range(node_num):
            if self.dfs_tree.isVisited[i] == False:
                self.dfs_tree.depth_first_search(i, self.adj_list)
    
        articulation_points_list = []
        # print('articulation_points is', end=" ")
        for index, value in enumerate(self.dfs_tree.isArticulation_point):
            if value ==  True:
                # print(index, end=" ")
                articulation_points_list.append(index)

        return articulation_points_list



def main(argv):
    with open("/home/p4/work_space/Biconnect/topology/searchable_topo.txt", "r") as f:

        #行ごとにすべて読み込んでリストデータにする
        adj_matrix = f.readlines()

        #行ごとに文字列で読み込んだデータを数値に変換
        for i in range(len(adj_matrix)):
            adj_matrix[i] = adj_matrix[i].split()
            for j in range(len(adj_matrix)):
                adj_matrix[i][j] = int(adj_matrix[i][j])

    adj_matrix = np.array(adj_matrix)

    graph = Topology(adj_matrix)
    articulation_points_list = graph.find_articulation_points(len(adj_matrix))
    print(articulation_points_list)
    print('\n')


    print(graph.dfs_tree.parent)
    print(graph.dfs_tree.search_order)




if __name__ == '__main__':
    sys.exit(main(sys.argv))

