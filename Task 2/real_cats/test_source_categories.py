import unittest
import pandas as pd
from train_source_categories import prepare,split


class SourceCategoryTests(unittest.TestCase):
    def test_other_categories_and_inactive_rows_are_excluded(self):
        b=pd.DataFrame({'address':['b','inactive'],'label':['benign','benign'],'transaction_number':[1,0]})
        c=pd.DataFrame({'address':['h','t','r'],'label':['Hack','Theft','Ransomware'],'transaction_number':[1,2,4]})
        self.assertEqual(set(prepare(b,c).address),{'b','h','t'})

    def test_conflicting_source_labels_rejected(self):
        b=pd.DataFrame({'address':['same'],'label':['benign'],'transaction_number':[1]})
        c=pd.DataFrame({'address':['same'],'label':['Hack'],'transaction_number':[2]})
        with self.assertRaises(ValueError):prepare(b,c)

    def test_three_way_split_is_disjoint_and_exhaustive(self):
        d=pd.DataFrame({'address':[str(i) for i in range(100)],'label':['benign']*60+['Hack']*20+['Theft']*20})
        parts=split(d);sets=[set(p) for p in parts]
        self.assertFalse(sets[0]&sets[1] or sets[0]&sets[2] or sets[1]&sets[2])
        self.assertEqual(len(set.union(*sets)),100)
        self.assertEqual([len(p) for p in parts],[60,20,20])


if __name__=='__main__':unittest.main()
