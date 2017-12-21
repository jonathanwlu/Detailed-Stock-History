import os.path as op
import pyodbc
import numpy as np
import pandas as pd
from pandas.io.sql import DatabaseError
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from datetime import date as dtdate
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib import cm
import matplotlib.pyplot as plt


def update():
    textbox.selectAll()
    textbox.setFocus()
    try:
        plot(textbox.text(), textbox2.text())
        print('updating')
        fig.canvas.draw_idle()
        return True
    except (DatabaseError, ValueError):
        print('one or more entries are invalid')
        return False


def plot(sym, date):
    fig.clear()
    with open(op.join('sql', 'VolSurf_S.sql'), 'r') as vs, open(op.join('sql', 'SymbHist.sql'), 'r') as sh:
        vs_sql = vs.read().replace('SYM1', sym.upper())
        sh_sql = sh.read().replace('SYM1', sym.upper()).replace('DATE1', date)
    vs_full_df = pd.read_sql_query(vs_sql, cnxn)
    sh_data = pd.read_sql_query(sh_sql, cnxn, index_col='TradeDate')
    if vs_full_df.empty or sh_data.empty:
        raise ValueError()
    spx = vs_full_df.loc[0, 'sPx']
    vs_data = vs_full_df.pivot('Strike', 'TDTE', 'IV').interpolate(method='piecewise_polynomial')

    plt.title(sym.upper())

    vs_ax = plot_vs(vs_data, spx)
    price_ax = plot_price(sh_data.loc[:, ['Px', 'SMA50', 'SMA200', 'EventType']])
    vol_ax = plot_vol(sh_data.loc[:, ['IV1M', 'IV3M', 'IVFar', 'TV', 'EventType']], price_ax)
    skew_ax = plot_skew(sh_data.loc[:, ['Skew3M', 'SkewFar', 'TVSkew', 'EventType']], price_ax)

    today = dtdate.today()
    fig.suptitle(f'{sym.upper()} {date}-{today.month}/{today.day}/{today.year}', fontsize=16, fontweight='bold')
    fig.subplots_adjust(left=0.035, right=1,
                        bottom=0.075, top=0.92,
                        hspace=0.4, wspace=0.1)


def plot_vs(data, spx):
    ax = plt.subplot2grid((5, 2), (0, 1), rowspan=5, facecolor='silver')
    data.plot(ax=ax, cmap='inferno', legend='none')
    plt.axvline(spx, c='white', ls='dashed')

    ax.set_title('Current IV')
    ax.set_xlabel('Strike')
    ax.set_ylabel('')
    ax.legend().set_visible(False)
    sm = cm.ScalarMappable(cmap='inferno', norm=plt.Normalize(vmin=data.columns.min(), vmax=data.columns.max()))
    sm.set_array([])
    plt.colorbar(sm, ax=ax).set_label('TDTE')
    return ax


def plot_price(data):
    ax = plt.subplot2grid((5, 2), (0, 0), rowspan=2, facecolor='silver')
    ax.plot(data['Px'], c='#1b9e77', lw=1)
    ax.plot(data['SMA50'], c='#d95f02', lw=1)
    ax.plot(data['SMA200'], c='#7570b3', lw=1)
    for date in data['EventType'].dropna().index:
        plt.axvline(date, c='white', ls='dashed', lw=0.5)

    ax.set_xlabel('')
    ax.set_ylabel('')
    leg = ax.legend(loc='best')
    for legobj in leg.legendHandles:
        legobj.set_linewidth(3)
    plt.setp(ax.get_xticklabels(), visible=False)
    ax.set_title('Price History')
    return ax


def plot_vol(data, shareax):
    ax = plt.subplot2grid((5, 2), (2, 0), rowspan=2, facecolor='silver', sharex=shareax)
    ax.plot(data['IV1M'], c='#1b9e77', lw=0.5)
    ax.plot(data['IV3M'], c='#d95f02', lw=0.5)
    ax.plot(data['IVFar'], c='#7570b3', lw=0.5)
    ax.plot(data['TV'], c='#e7298a', lw=0.5)
    for date in data['EventType'].dropna().index:
        plt.axvline(date, c='white', ls='dashed', lw=0.5)

    ax.set_ylabel('')
    leg = ax.legend(loc='best')
    for legobj in leg.legendHandles:
        legobj.set_linewidth(3)
    plt.setp(ax.get_xticklabels(), visible=False)
    ax.set_title('Vol History')
    return ax


def plot_skew(data, shareax):
    ax = plt.subplot2grid((5, 2), (4, 0), facecolor='silver', sharex=shareax)
    ax.plot(data['Skew3M'], c='#1b9e77', lw=0.5)
    ax.plot(data['SkewFar'], c='#d95f02', lw=0.5)
    ax.plot(data['TVSkew'], c='#7570b3', lw=1)
    for date in data['EventType'].dropna().index:
        plt.axvline(date, c='white', ls='dashed', lw=0.5)

    ax.set_ylabel('')
    leg = ax.legend(loc='best')
    for legobj in leg.legendHandles:
        legobj.set_linewidth(3)
    ax.set_title('Skew History')
    return ax


# def next_box():
#     textbox2.selectAll()
#     textbox2.setFocus()


def save_pic():
    if update():
        fig.savefig(op.join('out', textbox.text().upper() + '_' + textbox2.text().replace('/', '-') + '.png'))


cnxn = pyodbc.connect("Driver={SQL Server};Server=[server];UID=[user];PWD=[pw];Database=stocks;")

fig = plt.figure()

root = fig.canvas.manager.window
panel = QtWidgets.QWidget()
hbox = QtWidgets.QHBoxLayout(panel)

textbox = QtWidgets.QLineEdit(parent=panel)
textbox.returnPressed.connect(update)
hbox.addWidget(textbox)
hbox.addSpacing(10)

textbox2 = QtWidgets.QLineEdit(parent=panel)
textbox2.returnPressed.connect(update)
hbox.addWidget(textbox2)
hbox.addSpacing(10)

but1 = QtWidgets.QPushButton('Plot', parent=panel)
but1.clicked.connect(update)
hbox.addWidget(but1)
hbox.addSpacing(10)

but2 = QtWidgets.QPushButton('Save', parent=panel)
but2.clicked.connect(save_pic)
hbox.addWidget(but2)

panel.setLayout(hbox)

dock = QtWidgets.QDockWidget(parent=root)
dock.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
root.addDockWidget(Qt.BottomDockWidgetArea, dock)
dock.setWidget(panel)

toolbar = root.findChild(QtWidgets.QToolBar)
toolbar.setVisible(False)

root.setFixedSize(1280, 720)
root.statusBar().setSizeGripEnabled(False)

textbox.setText('SPY')
textbox2.setText('1/1/11')
textbox.selectAll()
textbox.setFocus()

update()
plt.show()
