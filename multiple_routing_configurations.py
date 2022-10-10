import queue
import sys
from typing import List

from normal_configuration import NormalConfiguration
from backup_configuration import BackupConfiguration
from constants import DIRECTORY_NAME, BACKUP_CONF_NUM

RESTRICT_WEIGHT = 1000
ISOLATE_WEIGHT = 100000


class MultipleRoutingConfigurations(object):
  def __init__(self, adj_matrix: List[int]) -> None:
    self.normal_conf = NormalConfiguration(adj_matrix)
    self.backup_conf = self._get_backup_conf(adj_matrix)

    self.node_queue = queue.Queue()
    self.priority_link_list = []
  
  def _get_backup_conf(self, adj_matrix: List[int]) -> List[int]:
    '''
    指定した数のバックアップルーティング構成オブジェクトを生成
    '''
    backup_conf = [None] * BACKUP_CONF_NUM
    for i in range(BACKUP_CONF_NUM):
      backup_conf[i] = BackupConfiguration(adj_matrix)
    return backup_conf
  
  def _get_isolated_configuration(self, node: int) -> int:
    '''
    指定したノードが他の構成で分離されているか確認

    :return i: int ノードが既に分離されているバックアップルーティング構成, 分離されていない場合は -1 を返す
    '''
    for i in range(BACKUP_CONF_NUM):
      if node in set(self.backup_conf[i].isolated_nodes_set):
        return i
    return -1
  

  def reorder_node_queue(self, isolated_node: int, next_isolating_node: int) -> None:
    '''
    分離するノードの順番を入れ替える

    MRCの制約上，ノードを分離した際に同じバックアップ構成で分離できないリンクが生じる
    その場合，次のバックアップ構成で先に分離することでMRCの制約をクリアする
    :params isolated_node: int あるバックアップ構成で分離したノード
    :params next_isolating_node: int 別のバックアップ構成で優先的に分離するノード
    '''
    node_queue_for_sorting = queue.Queue()

    while not self.node_queue.empty():
      tmp = self.node_queue.get()
      if tmp != next_isolating_node:
        node_queue_for_sorting.put(tmp)

    self.node_queue.put(next_isolating_node)

    while not node_queue_for_sorting.empty():
      self.node_queue.put(node_queue_for_sorting.get())
    


  def get_link_queue_for_sorting(self, next_isolating_conf: int) -> None:
    priority_link_num = len(self.priority_link_list)

    for _ in range(priority_link_num):
      next_isolating_node, isolating_node = self.priority_link_list.pop(0)
      isIsolated = False
      for conf_i in range(len(self.backup_conf)):
        if next_isolating_node in set(self.backup_conf[conf_i].isolated_nodes_set):
          isIsolated = True
          break

      if not isIsolated:
        self.backup_conf[next_isolating_conf].links_queue_for_sorting.put([next_isolating_node,isolating_node])


  def _get_link_queue_for_isolate(self, isolating_conf: int, isolating_node: int) -> None:
    '''
    指定したノードに接続されたリンクをキューに入れる

    キューの順番でリンクを分離していくため，優先したいリンクはこの時に先に入れておく
    '''
    priority_links = []
    priority_set = set()

    while not self.backup_conf[isolating_conf].links_queue_for_sorting.empty():
      priority_links.append(self.backup_conf[isolating_conf].links_queue_for_sorting.get())

    for i in range(len(priority_links)):
      if priority_links[i][0] == isolating_node:
        self.backup_conf[isolating_conf].connected_links_queue.put(priority_links[i])
      priority_set.add(priority_links[i][1])

    for i in range(len(self.backup_conf[isolating_conf].adj_matrix)):
      if i not in priority_set\
          and self.backup_conf[isolating_conf].adj_matrix[isolating_node][i] != 0:
        self.backup_conf[isolating_conf].connected_links_queue.put([isolating_node,i])


  def isolate_a_node(self, isolating_conf: int, node_to_isolate: int) -> None:
    '''
    :params isolating_conf: int 分離するバックアップルーティング構成の番号
    :parsms node_to_isolate: int 分離するノードの番号
    '''
    self._get_link_queue_for_isolate(isolating_conf, node_to_isolate)

    while not self.backup_conf[isolating_conf].connected_links_queue.empty():
      isolating_node, connected_node = self.backup_conf[isolating_conf].connected_links_queue.get()
      
      if isolating_node != node_to_isolate:
          continue

      # 対向のノードが分離されている構成番号（まだ分離されていない場合、-1）
      conf_already_isolate = self._get_isolated_configuration(connected_node)

      # 対向のノードが先に同じバックアップ構成で分離されている場合
      # - ノード間のリンクが制限リンクであれば，分離してしまうと，MRCの制約に反する
      # - ノード間のリンクが分離リンクであれば，分離可能
      if isolating_conf == conf_already_isolate:
        if self.backup_conf[conf_already_isolate].adj_matrix[isolating_node][connected_node] == RESTRICT_WEIGHT:
          return False
        else:
          self.backup_conf[isolating_conf].set_isolate_weight(isolating_node, connected_node)


      # 対向のノードが先に別のバックアップ構成で分離されており，
      # * そのバックアップ構成において，ノード間のリンクが制限リンクである場合
      #   - 制限リンクが接続されているか，通常ノードがまだ残っていることを確認して，分離する
      #   - 他に分離リンクしか接続されていない場合は，分離するとMRCの制約に反する
      # * 別のバックアップ構成において，ノード間のリンクが既に分離されている場合
      #   - ノード間のリンクを制限リンクにする
      elif 0 <= conf_already_isolate <= BACKUP_CONF_NUM:
        if self.backup_conf[conf_already_isolate].adj_matrix[isolating_node][connected_node] == RESTRICT_WEIGHT:
          if self.backup_conf[isolating_conf].can_isolate_a_link(isolating_node, connected_node):
              self.backup_conf[isolating_conf].set_isolate_weight(isolating_node, connected_node)
          else:
            return False

        elif self.backup_conf[conf_already_isolate].adj_matrix[isolating_node][connected_node] == ISOLATE_WEIGHT:
          self.backup_conf[isolating_conf].set_restrict_weight(isolating_node, connected_node)

        else:
          print('\nMRCのコードに問題が起きました\n')
          sys.exit()


      # 対向のノードがまだどの構成でも分離されていない場合
      # - 制限リンクが接続されているか，通常ノードがまだ残っていることを確認して，分離する
      # - 他に分離リンクしか接続されていない場合は，制限リンクにする
      elif conf_already_isolate == -1:
        if self.backup_conf[isolating_conf].can_isolate_a_link(isolating_node, connected_node):
            self.backup_conf[isolating_conf].set_isolate_weight(isolating_node, connected_node)
        else:
          self.backup_conf[isolating_conf].set_restrict_weight(isolating_node, connected_node)

          #　次のループで優先して分離するためにキューの順番を入れ替える
          self.reorder_node_queue(isolating_node, connected_node)
          #　優先して分離するリンクを追加
          self.priority_link_list.append([connected_node, isolating_node])


      else:
        print('\nMRCのコードに問題が起きました\n')
        sys.exit()
    
    return True


 # TODO 他のクラスに移動
  def export_adj_matrix(self, output_file_name: str) -> None:
    for i in range(len(self.backup_conf)):
      with open(output_file_name + str(i) + '.txt','w') as f:
        for row in range(len(self.normal_conf.adj_matrix)):
          for col in range(len(self.normal_conf.adj_matrix)):
              f.write("{:8}".format(int(self.backup_conf[i].adj_matrix[row][col])))
          f.write('\n')