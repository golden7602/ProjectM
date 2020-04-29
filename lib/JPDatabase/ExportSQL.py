from os import getcwd, path as ospath
from sys import path as jppath
jppath.append(getcwd())

from lib.JPDatabase.Database import JPDb
from decimal import Decimal
import datetime
from PyQt5.QtCore import QDate, pyqtSignal, QObject
from lib.JPFunction import JPDateConver


class CreateSQL_MySQL(QObject):
    exportOneRecord = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def getSql(self, tablename):

        sql = "select * from {fn}".format(fn=tablename)
        con = JPDb().currentConn
        cur = con.cursor()
        cur.execute(sql)
        con.commit()
        tab = cur._result.rows
        if len(tab)==0:
            return 
        c_col = len(cur._result.fields)
        fns = ['`{}`'.format(r.name) for r in cur._result.fields]
        fg = ", "
        sql_ins = 'INSERT INTO `{tn}` ({f}) VALUES \n{v};'
        values = []
        vs = []
        for r in range(len(tab)):
            d = tab[r]
            vs = []
            for col in range(c_col):
                v = d[col]
                if v is None:
                    vs.append('Null')
                    continue
                elif isinstance(v, str):
                    vs.append("'{}'".format(v.replace("'","\\'")))
                elif isinstance(v, (int, float, Decimal)):
                    vs.append('{}'.format(v))
                elif isinstance(v, bytes):
                    v = 0 if v == bytes([0]) else 1
                    vs.append('{}'.format(v))
                elif isinstance(v, (datetime.datetime, datetime.date)):
                    vs.append("'{}'".format(JPDateConver(v), str))
                else:
                    raise TypeError("没有该类型的转换器【{v}】={t}".format(v=fns[col],
                                                                t=type(v)))
            vs = [str(r) for r in vs]
            values.append('(' + fg.join(vs) + ')')
            self.exportOneRecord.emit()

        sql_ins = sql_ins.format(tn=tablename,
                                 f=fg.join(fns),
                                 v=(fg + '\n\t').join(values))
        return sql_ins


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    db = JPDb()
    db.setDatabaseType(1)
    app = QApplication(sys.argv)
    exp = CreateSQL_MySQL()
    print(exp.getSql("t_order"))