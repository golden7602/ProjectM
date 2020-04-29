import re
from functools import singledispatch
from os import getcwd, path as ospath
from sys import path as jppath
jppath.append(getcwd())

import datetime
from pymysql import connect as mysql_connect
from pymysql import cursors as mysql_cursors
from PyQt5.QtWidgets import QMessageBox

from lib.JPDatabase.Field import JPFieldInfo, JPMySQLFieldInfo
from lib.JPFunction import Singleton
from lib.JPConfigInfo import ConfigInfo


class JPDbType(object):
    MySQL = 1
    SqlServer = 2
    Acdess = 3


@Singleton
class JPDb(object):
    __init_times = 0
    __currentConn = None
    __db_type = None

    def __init__(self, dbtype=None):
        if self.__init_times == 0:
            self.__db_type = dbtype
            self.__currentConn = self.currentConn

        self.__init_times += 1

    def setDatabaseType(self, db_type: JPDbType):
        self.__db_type = db_type

    def close(self):
        """关闭数据库连接"""
        try:
            self.__currentConn.close()
        except Exception as e:
            print(str(e))

    @property
    def currentConn(self) -> mysql_connect:
        mConfigInfo = ConfigInfo()
        if self.__db_type == JPDbType.MySQL:
            if self.__currentConn is None:
                try:
                    conn = mysql_connect(host=mConfigInfo.host,
                                         user=mConfigInfo.user,
                                         password=mConfigInfo.password,
                                         database=mConfigInfo.database,
                                         port=mConfigInfo.port)
                except Exception as e:
                    linkErr = '连接数据库错误，请检查"config.ini"文件\n'
                    linkErr = linkErr + 'Connecting the database incorrectly, '
                    linkErr = linkErr + 'please check the "config.ini" file'
                    s = Exception.__repr__(e) + '\n' + linkErr
                    QMessageBox.warning(None, '错误', s, QMessageBox.Yes,
                                        QMessageBox.Yes)
                    exit()
                self.__currentConn = conn
            return self.__currentConn
        if self.__db_type == JPDbType.SqlServer:
            pass

        if self.__db_type == JPDbType.SqlServer:
            pass

    # 生成一个空对象
    def getFeildsInfoAndData(self, sql) -> JPFieldInfo:
        if self.__db_type == JPDbType.MySQL:
            con = cur = self.currentConn
            cur = con.cursor()
            try:
                cur.execute(sql)
                con.commit()
            except Exception as e:
                raise ValueError('SQL语句或表名格式不正确!\n{}\n'.format(sql) + str(e))

            covsdict = JPMySQLFieldInfo.getConvertersDict()
            flds = [JPMySQLFieldInfo(item) for item in cur._result.fields]
            rs = cur._result.rows
            cover = [covsdict[fld.TypeCode] for fld in flds]
            datas = []
            for i in range(len(rs)):
                datas.append([cover[j](v) for j, v in enumerate(rs[i])])
            return flds, datas

    def NewPkSQL(self, role_id: int):
        if self.__db_type == JPDbType.MySQL:
            sql1 = 'SELECT CONCAT(fPreFix,if(fHasDateTime,'
            sql1 = sql1 + 'DATE_FORMAT(CURRENT_DATE(),'
            sql1 = sql1 + 'replace(replace(replace(replace(fDateFormat,'
            sql1 = sql1 + "'yyyy','%Y'),'yy','%y')"
            sql1 = sql1 + ",'mm','%m'),'dd','%d')),'')"
            sql1 = sql1 + ',LPAD(fCurrentValue+1, fLenght , 0)) into @PK'
            sql1 = sql1 + ' FROM systabelautokeyroles'
            sql1 = sql1 + ' WHERE fRoleID={r_id};'
            sql1 = sql1.format(r_id=role_id)

            sql2 = "UPDATE systabelautokeyroles"
            sql2 = sql2 + " SET fCurrentValue=fCurrentValue+1, fLastKey=@PK"
            sql2 = sql2 + " WHERE fRoleID={r_id};"
            sql2 = sql2.format(r_id=role_id)

            sql3 = "SELECT @PK as NewID;"
            return [sql1, sql2, sql3]

    def LAST_INSERT_ID_SQL(self):
        if self.__db_type == JPDbType.MySQL:
            return 'SELECT LAST_INSERT_ID()'

    def getDataList(self, sql: str) -> list:
        if self.__db_type == JPDbType.MySQL:
            con = cur = self.currentConn
            cur = con.cursor()
            try:
                cur.execute(sql)
                con.commit()
            except Exception as e:
                raise ValueError('SQL语句或表名格式不正确!\n{}\n'.format(sql) + str(e))
        return [list(r) for r in cur._result.rows]

    def getDict(self, sql) -> dict:
        '''getDict(sql)
        此方法返回的数据可用于界面显示，数据类型进行了转换，其中
        Decimal 转换成了Float,datetime转换成了QDate
        '''
        if self.__db_type == JPDbType.MySQL:
            con = self.currentConn
            cur = con.cursor()
            try:
                cur.execute(sql)
                con.commit()
            except Exception as e:
                raise ValueError('SQL语句或表名格式不正确!\n{}\n'.format(sql) + str(e))

            rs = cur._result.rows
            flds = cur._result.fields
            datas = []
            for row in rs:
                dic_i = {}
                for n, v in zip(flds, row):
                    tp_i = JPMySQLFieldInfo.tp[n.type_code]
                    dic_i[n.name] = JPMySQLFieldInfo.getConvertersDict()[tp_i](v)
                datas.append(dic_i)

            # covsdict = JPMySQLFieldInfo.getConvertersDict()
            # flds = [JPMySQLFieldInfo(item) for item in cur._result.fields]
            # rs = cur._result.rows
            # cover = [covsdict[fld.TypeCode] for fld in flds]
            # datas = []
            # for i in range(len(rs)):
            #     datas.append({
            #         flds[j].FieldName: cover[j](v)
            #         for j, v in enumerate(rs[i])
            #     })
            return datas

    def getOnlyStrcFilter(self):
        if self.__db_type == JPDbType.MySQL:
            return " Limit 0"

    def executeTransaction(self, sqls):
        """执行一组语句，返回值两个
            第一个是执行状态，成功返回 True
            第二个是返回查询结果第一行，第一个字段的值（如果有返回值）,没有返回值则返回None
        """
        con = self.currentConn
        cur = con.cursor()
        con.begin()
        try:
            if isinstance(sqls, str):
                cur.execute(sqls)
            if isinstance(sqls, (list, tuple)):
                for sql in sqls:
                    sql_t = re.sub(r'^\s', '',
                                   re.sub(r'\s+', ' ', re.sub(r'\n', '', sql)))
                    cur.execute(sql_t)
        except Exception as e:
            con.rollback()
            QMessageBox.warning(None, '提示', "执行SQL出错！" + '\n' + str(e),
                                QMessageBox.Yes, QMessageBox.Yes)
            return False, None
        else:
            con.commit()
            if cur._rows:
                return True, cur._rows[0][0]
            else:
                return True, None

    def __getattr__(self, name):
        if name == '_JPDb__db_type':
            raise AttributeError("应在第一使用JPDb类时，先调用其setDatabaseType方法指定数据库类型")

    # def getOnConfigValue(self, name, vCls):
    #     tp = {
    #         str: "fValueStr",
    #         int: "fValueInt",
    #         bool: "fValueBool",
    #         datetime.date: "fValueDate",
    #         datetime.datetime: "fValueDateTime"
    #     }
    #     if not (vCls in tp.keys()):
    #         raise ValueError("给定参数类型不在列表中")
    #     sql = "select {tp} from sysconfig where fName='{name}'"
    #     sql = sql.format(tp=tp[vCls], name=name)
    #     r, r2 = self.executeTransaction(sql)
    #     if r2:
    #         return r2
    #     else:
    #         raise ValueError("取参数值错误")

    def saveConfigVale(self, name, value, vCls):
        tp = {
            str: "fValueStr",
            int: "fValueInt",
            bool: "fValueBool",
            datetime.date: "fValueDate",
            datetime.datetime: "fValueDateTime"
        }
        if not (vCls in tp.keys()):
            raise ValueError("给定参数类型不在列表中")
        sql1 = "insert into sysconfig (fName,{tp}) values ('{name}','{value}')"
        sql = "update sysconfig set {tp}='{value}' where fName='{name}'"
        sql = sql.format(tp=tp[vCls], value=value, name=name)
        r, r2 = self.executeTransaction(sql)
        if not r:
            raise ValueError("保存参数值错误")


if __name__ == "__main__":
    db = JPDb()
    db.setDatabaseType(1)
    print(JPDb().getOnConfigValue('Note_PrintingOrder', str))
