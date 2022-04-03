import 'package:flutter/material.dart';

import 'package:windshield/models/balance_sheet/balance_sheet.dart';
import 'package:windshield/models/balance_sheet/asset.dart';
import 'package:windshield/models/balance_sheet/debt.dart';

class BalanceSheetProvider extends ChangeNotifier {
  late BSheetBalance _bs;
  BSheetBalance get bs => _bs;

  int _pageIdx = 0;
  int get pageIdx => _pageIdx;

  double _assTotal = 0;
  double get assTotal => _assTotal;
  double _debtTotal = 0;
  double get debtTotal => _debtTotal;

  // ftype = 7
  List<BSheetAsset> _assLiquidList = [];
  List<BSheetAsset> get assLiquidList => _assLiquidList;
  double _assLiquidTotal = 0;
  double get assLiquidTotal => _assLiquidTotal;
  // 8
  List<BSheetAsset> _assInvestList = [];
  List<BSheetAsset> get assInvestList => _assInvestList;
  double _assInvestTotal = 0;
  double get assInvestTotal => _assInvestTotal;
  // 9
  List<BSheetAsset> _assPrivateList = [];
  List<BSheetAsset> get assPrivateList => _assPrivateList;
  double _assPrivateTotal = 0;
  double get assPrivateTotal => _assPrivateTotal;
  // 10
  List<BSheetDebt> _debtShortList = [];
  List<BSheetDebt> get debtShortList => _debtShortList;
  double _debtShortTotal = 0;
  double get debtShortTotal => _debtShortTotal;
  // 11
  List<BSheetDebt> _debtLongList = [];
  List<BSheetDebt> get debtLongList => _debtLongList;
  double _debtLongTotal = 0;
  double get debtLongTotal => _debtLongTotal;

  bool _needFetchAPI = false;
  bool get needFetchAPI => _needFetchAPI;

  get baltotal => null;

  void setBs(BSheetBalance value) {
    _bs = value;
  }

  void setPageIdx() {
    if (_pageIdx == 0) {
      _pageIdx = 1;
    } else {
      _pageIdx = 0;
    }
    notifyListeners();
  }

  void setBsType() {
    _assInvestTotal = 0;
    _assLiquidTotal = 0;
    _assPrivateTotal = 0;
    _debtShortTotal = 0;
    _debtLongTotal = 0;
    for (var item in _bs.assets) {
      if (item.cat.ftype == '7') {
        _assLiquidList.add(item);
        _assLiquidTotal += item.recentVal;
      } else if (item.cat.ftype == '8') {
        _assInvestList.add(item);
        _assInvestTotal += item.recentVal;
      } else if (item.cat.ftype == '9') {
        _assPrivateList.add(item);
        _assPrivateTotal += item.recentVal;
      }
    }
    for (var item in _bs.debts) {
      if (item.cat.ftype == '10') {
        _debtShortList.add(item);
        _debtShortTotal += item.balance;
      } else if (item.cat.ftype == '11') {
        _debtLongList.add(item);
        _debtLongTotal += item.balance;
      }
    }
    _assTotal = _assLiquidTotal + _assInvestTotal + _assPrivateTotal;
    _debtTotal = _debtShortTotal + _debtLongTotal;
    notifyListeners();
  }

  void setNeedFetchAPI() {
    _needFetchAPI = !_needFetchAPI;
    notifyListeners();
  }
}
