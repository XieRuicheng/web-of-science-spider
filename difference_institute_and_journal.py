
# -*- coding: utf-8 -*-

'''
name:       difference_institute_and_journal.py
usage:      --
author:     Ruicheng
date:       2020-10-17 18:20:49
version:    1.0
Env.:       Python 3.7.3, WIN 10
'''

import re
import yaml


def sort_IF(x, y):
    if x['IF'] < y['IF']:
        return -1
    if x['IF'] == y['IF']:
        return 0
    else:
        return 1

source_name = 'Oct17_16_29_result.yaml'
with open(f'./result/{source_name}', 'r') as fp:
    records_dict = yaml.load(fp, Loader=yaml.FullLoader)

# remove prefix of institute like '[ 1 ] '
prefix_re = re.compile('^\s*\[\s*?\d+?\s*?\]\s*')
# remove conference whose name contain digital
conference_re = re.compile('\d+')

journal_list = []
institute_list = []
author_list = []
sci_journal_other_IF = []
sci_journal_other = []
for record in records_dict.values():
    if record['Citation'] == 0:
        continue
    for citation in record['CiteDetail']:
        institute_list += citation['address']
        author_list += citation['authors']
        journal_list.append(citation['journal'])
        # journal other citations
        if ('Yang, Yunyun' not in citation['authors']) and (float(citation['IF']) > 0):
            sci_journal_other_IF.append({
                'journal': citation['journal'],
                'IF': citation['IF'],
            })
            sci_journal_other.append(citation['journal'])

# remove prefix of institute like '[ 1 ] '
institute_list = [prefix_re.sub('', x) for x in institute_list]

journal_set = set(journal_list)
author_set = set(author_list)
institute_set = set(institute_list)
sci_journal_other = set(sci_journal_other)

citation_unique_dict = {
    'author': sorted(list(author_set)),
    'institute': sorted(list(institute_set)),
    'journal_all': sorted(list(journal_set)),
    'journal_other_sci': sorted(list(sci_journal_other)),
    'journal_other_citation': sorted(sci_journal_other_IF, key=lambda x: x['IF'], reverse=True),
}

save_name = source_name.replace('result', 'institute_journal_author')
with open(f'./result/{save_name}', 'w') as fp:
    yaml.dump(citation_unique_dict, fp)


# save without citation detail
records_without_cite = {}
for key, val in records_dict.items():
    new_val = records_dict[key].copy()
    del new_val['CiteDetail']
    key_num = int(key[5:])
    new_key = f'paper-{key_num:02d}'
    records_without_cite[new_key] = new_val

save_name = source_name.replace('result', 'result_without_citation')
with open(f'./result/{save_name}', 'w') as fp:
    yaml.dump(records_without_cite, fp)
