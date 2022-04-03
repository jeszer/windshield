import 'package:dio/dio.dart';
import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:intl/intl.dart';
import 'package:jwt_decode/jwt_decode.dart';
import 'package:flutter/material.dart';

import '../../models/daily_flow/flow.dart';
import '../../models/statement/budget.dart';
import '../../models/user.dart';
import '../../models/provinces.dart';
import '../../models/statement/statement.dart';
import '../../models/statement/category.dart';
import '../../models/daily_flow/category.dart';
import '../../models/balance_sheet/balance_sheet.dart';

class Api extends ChangeNotifier {
  Dio dio = Dio();
  String? _accessToken;
  User? _user = User();
  bool _isLoggedIn = false;

  String? get accessToken => _accessToken;
  User? get user => _user;
  bool get isLoggedIn => _isLoggedIn;

  final _storage = const FlutterSecureStorage();

  Api() {
    dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        if (!options.path.contains('http')) {
          options.path = 'http://192.168.1.9:8000' + options.path;
        }
        options.headers['Authorization'] = 'JWT $_accessToken';
        if (options.path.contains('/user/register/') ||
            options.path.contains('/token/') ||
            options.path.contains('/token/refresh/')) {
          options.headers['Authorization'] = '';
        }
        // print(options.path + ' | ' + _accessToken.toString());
        print(options.path);
        return handler.next(options);
      },
      onError: (DioError error, handler) async {
        print(error.response);
        if (error.requestOptions.path.contains('token/refresh')) {
          _accessToken = null;
          await _storage.deleteAll();
          _isLoggedIn = false;
          notifyListeners();
          return handler.reject(error);
        }

        if (error.response?.statusCode == 401 &&
            error.response?.statusMessage == 'Unauthorized') {
          final refresh = await _storage.read(key: 'refreshToken');

          if (refresh != null) {
            if (Jwt.isExpired(refresh)) {
              _accessToken = null;
              await _storage.deleteAll();
              _isLoggedIn = false;
              notifyListeners();
              return handler.reject(error);
            } else {
              try {
                await refreshToken();
                return handler.resolve(await _retry(error.requestOptions));
              } catch (e) {
                print('FUCK MY LIFE');
              }
            }
          } else {
            _accessToken = null;
            await _storage.deleteAll();
            _isLoggedIn = false;
            notifyListeners();
            return handler.reject(error);
          }
        }

        return handler.next(error);
      },
    ));
  }

  Future<Response<dynamic>> _retry(RequestOptions requestOptions) async {
    final options = Options(
      method: requestOptions.method,
      headers: requestOptions.headers,
    );
    final data = dio.request<dynamic>(
      requestOptions.path,
      data: requestOptions.data,
      queryParameters: requestOptions.queryParameters,
      options: options,
    );
    return data;
  }

  Future<void> refreshToken() async {
    final refreshToken = await _storage.read(key: 'refreshToken');
    final response =
        await dio.post('/token/refresh/', data: {'refresh': refreshToken});
    if (response.statusCode == 200) {
      _accessToken = response.data['access'];
      await _storage.write(
          key: 'refreshToken', value: response.data['refresh']);

      // _isLoggedIn = true;
      // notifyListeners();
    }
  }

  Future<bool> login(String username, String password) async {
    try {
      final res = await dio.post(
        '/token/',
        data: {
          'user_id': username,
          'password': password,
        },
      );
      _accessToken = res.data['access'];
      await _storage.write(key: 'refreshToken', value: res.data['refresh']);
      Map<String, dynamic> data = Jwt.parseJwt(res.data['access']);

      _user?.uuid = data['user_id'];
      _isLoggedIn = true;
      notifyListeners();
      return true;
    } catch (e) {
      return false;
    }
  }

  Future<bool> loginByPin(String pin) async {
    try {
      final refresh = await _storage.read(key: 'refreshToken');
      final res = await dio.post('/token/refresh/', data: {'refresh': refresh});
      _accessToken = res.data['access'];
      await _storage.write(key: 'refreshToken', value: res.data['refresh']);
      Map<String, dynamic> data = Jwt.parseJwt(res.data['access']);
      _user?.uuid = data['user_id'];
      await getUserInfo();
      if (_user?.pin == pin) {
        _isLoggedIn = true;
        notifyListeners();
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  Future<void> logout() async {
    await _storage.deleteAll();
    _user = User();
    _accessToken = null;
    _isLoggedIn = false;
    notifyListeners();
  }

  Future<bool> register(
      String username, String password, String email, String phone) async {
    try {
      await dio.post(
        '/user/register/',
        options: Options(
          headers: {'Authorization': ''},
        ),
        data: {
          'user_id': username,
          'password': password,
          'email': email,
          'tel': phone,
        },
      );
      final res = await dio.post(
        '/token/',
        data: {
          'user_id': username,
          'password': password,
        },
      );

      _accessToken = res.data['access'];
      await _storage.write(key: 'refreshToken', value: res.data['refresh']);
      Map<String, dynamic> data = Jwt.parseJwt(res.data['access']);
      _user?.uuid = data['user_id'];
      return true;
    } catch (e) {
      return false;
    }
  }

  Future<User?> getUserInfo() async {
    try {
      final res = await dio.get('/user/${_user?.uuid}');
      // Map<String, dynamic> data = await jsonDecode(res.toString());
      print(res.data);
      _user = User.fromJson(res.data);
      print(_user);
      return _user;
    } catch (e) {
      print(e);
      return _user;
    }
  }

  Future<bool> updatePin(String pin) async {
    try {
      await dio.patch(
        '/user/${_user?.uuid}/',
        data: {
          'pin': pin,
        },
      );
      return true;
    } catch (e) {
      return false;
    }
  }

  Future<bool> updateUser(
      String province, String status, String occuType, int family) async {
    try {
      await dio.patch(
        '/user/${_user?.uuid}/',
        data: {
          "province": province,
          "status": status,
          "family": family.toString(),
          "occu_type": occuType,
        },
      );
      _isLoggedIn = true;
      notifyListeners();
      return true;
    } catch (e) {
      return false;
    }
  }

  Future<List<Province>?> getProvinces() async {
    try {
      final res = await dio.get('/api/provinces/');
      final data = (res.data as List).map((i) => Province.fromJson(i)).toList();
      return data;
    } catch (e) {
      return null;
    }
  }

  //แผนงบการเงิน
  Future<List<StmntStatement>> getAllNotEndYetStatements(DateTime date) async {
    try {
      final str = DateFormat('y-MM-dd').format(date);
      final res = await dio.get('/api/statement/?lower-date=$str');
      final data =
          (res.data as List).map((i) => StmntStatement.fromJson(i)).toList();
      return data;
    } catch (e) {
      return [];
    }
  }

  Future<List<StmntCategory>> getAllCategories(bool asUsed) async {
    try {
      final res = await dio
          .get('/api/categories/?as_used=${asUsed ? "True" : "False"}');
      final data =
          (res.data as List).map((i) => StmntCategory.fromJson(i)).toList();
      return data;
    } catch (e) {
      return [];
    }
  }

  Future<String> createStatement(
    String name,
    DateTime start,
    DateTime end,
  ) async {
    try {
      final res = await dio.post(
        '/api/statement/',
        data: {
          "name": name,
          "start": DateFormat('y-MM-dd').format(start),
          "end": DateFormat('y-MM-dd').format(end),
          "month": 1,
        },
      );
      return res.data['id'];
    } catch (e) {
      return '';
    }
  }

  Future<bool> deleteStatement(String id) async {
    try {
      final res = await dio.delete('/api/statement/$id/');

      return true;
    } catch (e) {
      return false;
    }
  }

  Future<bool> updateStatementName(String id, String name) async {
    try {
      await dio.patch('/api/statement/$id/name/', data: {"name": name});
      return true;
    } catch (e) {
      return false;
    }
  }

  Future<bool> updateStatementActive(String id) async {
    try {
      await dio.patch('/api/statement/$id/');
      return true;
    } catch (e) {
      return false;
    }
  }

  Future<bool> createBudgets(List<StmntBudget> budgets, String id) async {
    try {
      final data = budgets.map((e) {
        e.fplan = id;
        return e.toJson();
      }).toList();
      await dio.post(
        '/api/budget/',
        data: data,
      );
      return true;
    } catch (e) {
      return false;
    }
  }

  Future<bool> updateBudgets(List<StmntBudget> budgets, String id) async {
    try {
      final data = budgets.map((e) => e.toJsonUpdate()).toList();
      await dio.patch(
        '/api/budget/update/',
        data: data,
      );
      return true;
    } catch (e) {
      return false;
    }
  }

  Future<bool> deleteBudgets(List<String> budgets) async {
    try {
      await dio.delete('/api/budget/delete/', data: budgets);
      return true;
    } catch (e) {
      return false;
    }
  }

  //รายรับ-รายจ่าย
  Future<String> getTodayDFId() async {
    try {
      final res = await dio.get('/api/daily-flow-sheet/');
      return res.data['id'];
    } catch (e) {
      return '';
    }
  }

  Future<List<DFlowCategory>> getAllCategoriesWithBudgetFlows(
      DateTime date) async {
    try {
      final str = DateFormat('y-MM-dd').format(date);
      final res = await dio
          .get('/api/categories-budgets-flows/?as_used=True&date=$str');
      final data =
          (res.data as List).map((i) => DFlowCategory.fromJson(i)).toList();
      return data;
    } catch (e) {
      print(e);
      return [];
    }
  }

  Future<DFlowFlow> addFlow(
      String dfId, String catId, String name, double value, int method) async {
    try {
      final res = await dio.post(
        '/api/daily-flow/',
        data: {
          "df_id": dfId,
          "category": catId,
          "name": name,
          "value": value,
          "method": method,
        },
      );
      final data =
          (res.data as List).map((i) => DFlowFlow.fromJson(i)).toList();
      return data[0];
    } catch (e) {
      return DFlowFlow(
        id: '',
        method: Method(id: 0, name: '', icon: ''),
        name: '',
        value: 0,
        detail: '',
        dfId: '',
        cat: Cat(
          id: '',
          name: '',
          usedCount: 0,
          icon: '',
          ftype: '',
        ),
      );
    }
  }

  Future<DFlowFlow> editFlow(
      String id, String name, double value, int method) async {
    try {
      final res = await dio.patch(
        '/api/daily-flow/$id/',
        data: {
          "name": name,
          "value": value,
          "method": method,
        },
      );
      final data = DFlowFlow.fromJson(res.data);
      return data;
    } catch (e) {
      return DFlowFlow(
        id: '',
        method: Method(id: 0, name: '', icon: ''),
        name: '',
        value: 0,
        detail: '',
        dfId: '',
        cat: Cat(id: '', name: '', usedCount: 0, icon: '', ftype: ''),
      );
    }
  }

  Future<String> deleteFlow(String id) async {
    try {
      final res = await dio.delete('/api/daily-flow/$id/');
      final data = DFlowFlow.fromJson(res.data);
      return data.id;
    } catch (e) {
      return '';
    }
  }

  //งบดุลการเงิน
  Future<BSheetBalance?> getBalanceSheet() async {
    try {
      final res = await dio.get('/api/balance-sheet/');
      final data = BSheetBalance.fromJson(res.data);
      return data;
    } catch (e) {
      print(e);
      return null;
    }
  }
}
