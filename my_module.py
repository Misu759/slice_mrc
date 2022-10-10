import random
import matplotlib.pyplot as plt

def from_file_to_adj_matrix(file_name):
    with open(file_name, "r") as f:

        adj_matrix = f.readlines()
        for i in range(len(adj_matrix)):
            adj_matrix[i] = adj_matrix[i].split()
            for j in range(len(adj_matrix)):
                adj_matrix[i][j] = int(adj_matrix[i][j])

    return adj_matrix


def from_adj_matrix_to_file(adj_matrix, file_name):
    with open(file_name,'w') as f:
        for row in range(len(adj_matrix)):
            for col in range(len(adj_matrix)):
                f.write("{:2}".format(int(adj_matrix[row][col])))
            f.write('\n')

# Random int value generation without duplicates
def rand_ints_nodup(a, b, k):
    ns = []
    while len(ns) < k:
        n = random.randint(a, b)
        if not n in ns:
            ns.append(n)
    return ns



def plot_graph(x, y, comparison_y, x_label, y_label, xtick_list, ytick_list, output_file):
    plt.rcParams['figure.subplot.bottom'] = 0.15
    plt.rcParams['figure.subplot.left'] = 0.15
    plt.plot(x, y, marker="o", color = "red", label="proposal")
    plt.plot(x, comparison_y, marker="v", color = "blue", linestyle = ":", label="physical network");
    plt.rc('legend', fontsize=14)
    plt.xticks(xtick_list, fontsize=14)
    plt.yticks(ytick_list, fontsize=14)
    plt.xlabel(x_label, fontsize=18)
    plt.ylabel(y_label, fontsize=18)
    plt.grid(True)
    plt.legend(loc="lower right")
    plt.savefig(output_file, format="pdf", dpi=300)
    plt.show()