# -*- coding: utf-8 -*-


class JPExceptionFieldNull(Exception):
    def __init__(self, objname):
        """主表字段为空"""

        errstr = '字段【{fn}】的值不能为空！\n'
        errstr = errstr + 'Field [{fn}] cannot be empty!'
        self.Message = errstr.format(fn=objname)

    def __str__(self):
        return self.Message


class JPExceptionRowDataNull(Exception):
    def __init__(self, row_and_columnname, msg=None):
        """子表字段为空"""
        errstr = '第{row}行【{fn}】字段的值不能为空！\n'
        errstr = errstr + 'Row {row} field [{fn}] cannot be empty!'
        self.Row = row_and_columnname[0]
        self.Message = errstr.format(row=row_and_columnname[0],
                                     fn=row_and_columnname[1])

    def __str__(self):
        return self.Message
