class DepthFirstSearchTree(object):

    def __init__(self, node_num) -> None:
        self.search_count = 0
        self.isVisited = [False] * (node_num)
        self.search_order = [float("Inf")] * (node_num)
        self.low_link = [float("Inf")] * (node_num)
        self.parent = [-1] * (node_num)
        self.isArticulation_point = [False] * (node_num)

    def depth_first_search(self, node_u, adj_list):
        """
        return: None
        """
        children_counter = 0
        self.isVisited[node_u] = True

        self.search_order[node_u] = self.search_count
        self.low_link[node_u] = self.search_count
        self.search_count += 1

        for node_v in adj_list[node_u]:
            if self.isVisited[node_v] == False:
                self.parent[node_v] = node_u
                children_counter += 1
                self.depth_first_search(node_v, adj_list)

                self.low_link[node_u] = min(self.low_link[node_u], self.low_link[node_v])

                if self.parent[node_u] == -1 and children_counter > 1:
                    self.isArticulation_point[node_u] = True

                if self.parent[node_u] != -1 and self.low_link[node_v] >= self.search_order[node_u]:
                    self.isArticulation_point[node_u] = True

            elif node_v != self.parent[node_u]:
                self.low_link[node_u] = min(self.low_link[node_u], self.search_order[node_v])


    