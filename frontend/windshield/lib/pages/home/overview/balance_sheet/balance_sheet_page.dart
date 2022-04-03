import 'package:auto_route/auto_route.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:percent_indicator/circular_percent_indicator.dart';
import 'package:windshield/main.dart';
import 'package:windshield/models/balance_sheet/balance_sheet.dart';
import 'package:windshield/models/daily_flow/flow.dart';
import 'package:windshield/styles/theme.dart';
import 'package:percent_indicator/percent_indicator.dart';
import 'package:badges/badges.dart';
import 'package:windshield/routes/app_router.dart';
import 'package:windshield/utility/icon_convertor.dart';

final apiBSheet = FutureProvider.autoDispose<BSheetBalance?>((ref) async {
  ref.watch(provBSheet.select((value) => value.needFetchAPI));
  final data = await ref.read(apiProvider).getBalanceSheet();
  ref.read(provBSheet).setBs(data!);
  ref.read(provBSheet).setBsType();
  return data;
  

});

class BalanceSheetPage extends ConsumerWidget {
  const BalanceSheetPage({Key? key}) : super(key: key);
  

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    //ของจริง apiBsheet
    final api = ref.watch(apiBSheet);
    //final api = ref.watch(apiDFlow);
    return api.when(
      error: (error, stackTrace) => Text(stackTrace.toString()),
      loading: () => const Center(child: CircularProgressIndicator()),
      data: (_) {
        return Scaffold(
          body: Column(
            
            children: [
              
              AssetHomepage(),

              Container(
                height: 20,
              ),

              //แสดง widget หนี้สิน กับ ทรัพย์สิน

              SizedBox(
                  child: Row(children: [
                const Assettable(),
                const Depttable(),
              ])),

              //แสดงผล widget ส่วนล่าง

              Expanded(
              child: SingleChildScrollView(
                  child: Column(children: [
                Container(
                    // autofocusheight: 560,
                    child: Column(children: [
                      const LiqAssetTab(),
                      const IncOtherTab(),
                      const IncAssetTab(),
                    ])),
              ]))),
              //Container(color: Colors.black, height: 170),
              /* 
              SizedBox(child: Column(children: [
              const LiqAssetTab(),
              const ExpConTab(),
              const ExpNonConTab(),
              ])),*/

              //ปุ่มย้อนกลับ
              SizedBox(
                height: 75,
                child: Align(
                  alignment: Alignment.centerLeft,
                  child: TextButton.icon(
                    label: Text(
                      'ย้อนกลับ  ',
                      style: MyTheme.whiteTextTheme.headline3,
                    ),
                    icon: const Icon(
                      Icons.arrow_left,
                      color: Colors.white,
                    ),
                    style: TextButton.styleFrom(
                      backgroundColor: MyTheme.primaryMajor,
                      shape: const RoundedRectangleBorder(
                        borderRadius: BorderRadius.only(
                          topRight: Radius.circular(20),
                          bottomRight: Radius.circular(20),
                        ),
                      ),
                    ),
                    onPressed: () => AutoRouter.of(context).pop(),
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class AssetHomepage extends ConsumerWidget {
  const AssetHomepage({Key? key}) : super(key: key);
  

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    //final incTotal = ref.watch(provDFlow.select((e) => e.incTotal));
    final baltotal = ref.watch(provBSheet.select((e) => e.baltotal));
    
    var now = new DateTime.now();
    DateTime date = new DateTime(now.year, now.month, now.day);

    return Container(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: const [
                Padding(
                  padding: EdgeInsets.fromLTRB(25.0, 20.0, 0.0, 0.0),
                  child: Text(
                    'งบดุลการเงินของคุณ',
                    style: TextStyle(
                        color: Colors.white,
                        fontSize: 25,
                        decoration: TextDecoration.none),
                  ),
                ),
              ],
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(25.0, 35.0, 0.0, 0.0),
              child: Text(
                //วันที่
                '$date \n'+'ความมั่งคั่งสุทธิ',
                style: TextStyle(
                    color: Colors.white.withOpacity(0.7),
                    fontSize: 12,
                    decoration: TextDecoration.none
                    //Theme.of(context).textTheme.bodyText1,
                    ),
              ),
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Padding(
                  padding: const EdgeInsets.fromLTRB(25.0, 5.0, 0.0, 0.0),
                  child: Text(
                    '$baltotal',
                    style: const TextStyle(
                        color: Colors.white,
                        fontSize: 30,
                        decoration: TextDecoration.none
                        //Theme.of(context).textTheme.bodyText1,
                        ),
                  ),
                ),
                SizedBox(
                  child: Row(
                    children: [
                      Icon(
                        Icons.date_range,
                        size: 20.0,
                        color: MyTheme.secondaryMinor,
                      ),
                      Padding(
                        padding: const EdgeInsets.all(8.0),
                        child: Text(
                          //แก้วันที่ตรงนี้
                          'ข้อมูลล่าสุด\n',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w700,
                            color: MyTheme.secondaryMinor,
                          ),
                        ),
                      ),
                      Icon(
                        Icons.arrow_right,
                        size: 40.0,
                        color: MyTheme.secondaryMinor,
                      )
                    ],
                  ),
                )
              ],
            ),
          ],
        ),
        //Text('\n\nงบดุลของคุณ \n วันที่ 4 มีนาคม 2565 \n xxxxx บ.',style: MyTheme.whiteTextTheme.headline3),

        height: 180,
        width: 500,
        decoration: BoxDecoration(
          gradient: const LinearGradient(
              begin: Alignment.centerLeft,
              end: Alignment.centerRight,
              colors: [
                Color.fromARGB(255, 82, 54, 255),
                Color.fromARGB(255, 117, 161, 227),
              ]),
          //borderRadius: BorderRadius.circular(10),
        ));
  }
}

class Assettable extends ConsumerWidget {
  const Assettable({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Expanded(
      child: Container(
        decoration: BoxDecoration(
          gradient: const LinearGradient(
              begin: Alignment.centerLeft,
              end: Alignment.centerRight,
              colors: [
                Color.fromARGB(255, 52, 186, 216),
                Color.fromARGB(255, 56, 91, 206),
              ]),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            CircularPercentIndicator(
              radius: 25,
              progressColor: Colors.white,
              percent: 1,
              animation: true,
              animationDuration: 2000,
              lineWidth: 6.5,
              center: const Text('xx.x%',
                  style: TextStyle(color: Colors.white, fontSize: 11)),
              backgroundColor: const Color(0x80ffffff),
            ),
            Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  'สินทรัพย์',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.8),
                    fontSize: 15,
                  ),
                ),
                const Text(
                  'xxxxx บ.',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 25,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

//depttable
class Depttable extends ConsumerWidget {
  const Depttable({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Expanded(
      child: Container(
        decoration: BoxDecoration(
          gradient: const LinearGradient(
              begin: Alignment.centerLeft,
              end: Alignment.centerRight,
              colors: [
                Color(0xffee3884),
                Color(0xffab47bc),
              ]),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            CircularPercentIndicator(
              radius: 25,
              progressColor: Colors.white,
              percent: 0.744,
              animation: true,
              animationDuration: 2000,
              lineWidth: 6.5,
              center: Text('xx.x%',
                  style: TextStyle(color: Colors.white, fontSize: 11)),
              backgroundColor: const Color(0x80ffffff),
            ),
            Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  'หนี้สิน',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.8),
                    fontSize: 15,
                  ),
                ),
                const Text(
                  'xxxxx บ.',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 25,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class LiqAssetTab extends ConsumerWidget {
  const LiqAssetTab({Key? key}) : super(key: key);

  get incWorking => null;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final incWorkingList = ref.watch(provDFlow.select((e) => e.incWorkingList));

    return Padding(
      padding: const EdgeInsets.all(25.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('สินทรัพย์สภาพคล่อง', style: MyTheme.textTheme.headline3),
          GridView.builder(
            physics: const ScrollPhysics(),
            shrinkWrap: true,
            itemCount: incWorkingList.length,
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 4,
              mainAxisSpacing: 10,
              crossAxisSpacing: 10,
              mainAxisExtent: 100,
            ),
            itemBuilder: (_, index) {
              return Column(
                children: [
                  Expanded(
                    child: Badge(
                      position: BadgePosition(top: 0, end: 10, isCenter: false),
                      animationType: BadgeAnimationType.scale,
                      showBadge:
                          incWorkingList[index].flows.isEmpty ? false : true,
                      badgeContent: Text(
                        '${incWorkingList[index].flows.length}',
                        style: const TextStyle(fontSize: 15),
                      ),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          SizedBox(
                            height: 75, //height of button
                            width: 75, //width of button
                            child: ElevatedButton(
                              onPressed: () {
                                ref
                                    .read(provDFlow)
                                    .setColorBackground('income');
                                ref
                                    .read(provDFlow)
                                    .setCurrCat(incWorkingList[index]);
                                AutoRouter.of(context)
                                    .push(const DailyFlowCreateRoute());
                                ref.watch(provDFlow).currCat.flows;
                              },
                              style: ElevatedButton.styleFrom(
                                elevation: 0.0,
                                shadowColor: Colors
                                    .transparent, //remove shadow on button
                                primary: incWorkingList[index].budgets.isEmpty
                                    ? Color(0xffE0E0E0)
                                    : MyTheme.positiveMajor,
                                textStyle: const TextStyle(fontSize: 12),
                                padding: const EdgeInsets.all(10),

                                shape: const CircleBorder(),
                              ),
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(
                                    HelperIcons.getIconData(
                                        incWorkingList[index].icon),
                                    color: Colors.white,
                                  ),
                                  if (incWorkingList[index]
                                      .flows
                                      .isNotEmpty) ...[
                                    Text(
                                      _loopFlow(incWorkingList[index].flows),
                                    ),
                                  ],
                                ],
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  Text(incWorkingList[index].name)
                ],
              );
            },
          ),
        ],
      ),
    );
  }
}

class IncAssetTab extends ConsumerWidget {
  const IncAssetTab({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final incAssetList = ref.watch(provDFlow.select((e) => e.incAssetList));
    return Padding(
      padding: const EdgeInsets.all(25.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('รายรับจากการทำงาน', style: MyTheme.textTheme.headline3),
          GridView.builder(
            physics: const ScrollPhysics(),
            shrinkWrap: true,
            itemCount: incAssetList.length,
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 4,
              mainAxisSpacing: 10,
              crossAxisSpacing: 10,
              mainAxisExtent: 100,
            ),
            itemBuilder: (_, index) {
              return Column(
                children: [
                  Expanded(
                    child: Badge(
                      position: BadgePosition(top: 0, end: 10, isCenter: false),
                      animationType: BadgeAnimationType.scale,
                      showBadge:
                          incAssetList[index].flows.isEmpty ? false : true,
                      badgeContent: Text(
                        '${incAssetList[index].flows.length}',
                        style: const TextStyle(fontSize: 15),
                      ),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          SizedBox(
                            height: 75, //height of button
                            width: 75, //width of button
                            child: ElevatedButton(
                              onPressed: () {
                                ref
                                    .read(provDFlow)
                                    .setColorBackground('income');
                                ref
                                    .read(provDFlow)
                                    .setCurrCat(incAssetList[index]);
                                AutoRouter.of(context)
                                    .push(const DailyFlowCreateRoute());
                                ref.watch(provDFlow).currCat.flows;
                              },
                              style: ElevatedButton.styleFrom(
                                elevation: 0.0,
                                shadowColor: Colors
                                    .transparent, //remove shadow on button
                                primary: incAssetList[index].budgets.isEmpty
                                    ? Color(0xffE0E0E0)
                                    : MyTheme.positiveMajor,
                                textStyle: const TextStyle(fontSize: 12),
                                padding: const EdgeInsets.all(10),

                                shape: const CircleBorder(),
                              ),
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(
                                    HelperIcons.getIconData(
                                        incAssetList[index].icon),
                                    color: Colors.white,
                                  ),
                                  if (incAssetList[index].flows.isNotEmpty) ...[
                                    Text(
                                      _loopFlow(incAssetList[index].flows),
                                    ),
                                  ],
                                ],
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  Text(incAssetList[index].name)
                ],
              );
            },
          ),
        ],
      ),
    );
  }
}

class IncOtherTab extends ConsumerWidget {
  const IncOtherTab({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final incOtherList = ref.watch(provDFlow.select((e) => e.incOtherList));
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('รายรับอื่นๆ', style: MyTheme.textTheme.headline3),
        GridView.builder(
          physics: const ScrollPhysics(),
          shrinkWrap: true,
          itemCount: incOtherList.length,
          gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
            maxCrossAxisExtent: 100,
            mainAxisSpacing: 10,
            crossAxisSpacing: 10,
          ),
          itemBuilder: (_, index) {
            return Column(
              children: [
                Badge(
                  animationType: BadgeAnimationType.scale,
                  showBadge: incOtherList[index].flows.isEmpty ? false : true,
                  badgeContent: Text(
                    '${incOtherList[index].flows.length}',
                    style: const TextStyle(fontSize: 15),
                  ),
                  child: Column(
                    children: [
                      ElevatedButton(
                        onPressed: () {
                          ref.read(provDFlow).setColorBackground('income');
                          ref.read(provDFlow).setCurrCat(incOtherList[index]);
                          AutoRouter.of(context).push(DailyFlowCreateRoute());
                        },
                        style: ElevatedButton.styleFrom(
                          elevation: 0.0,
                          shadowColor:
                              Colors.transparent, //remove shadow on button
                          primary: incOtherList[index].budgets.isEmpty
                              ? MyTheme.positiveMinor
                              : MyTheme.positiveMajor,
                          textStyle: const TextStyle(
                              fontSize: 30, fontWeight: FontWeight.bold),
                          padding: const EdgeInsets.symmetric(
                              horizontal: 20, vertical: 20),

                          shape: const CircleBorder(),
                        ),
                        child: Column(
                          //mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              HelperIcons.getIconData(incOtherList[index].icon),
                              color: Colors.white,
                            ),
                            if (incOtherList[index].flows.isNotEmpty) ...[
                              Text(
                                _loopFlow(incOtherList[index].flows),
                              ),
                            ],
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                Text(incOtherList[index].name)
              ],
            );
          },
        ),
      ],
    );
  }
}

class ExpConTab extends ConsumerWidget {
  const ExpConTab({Key? key}) : super(key: key);

//add savind Class

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final expConList = ref.watch(provDFlow.select((e) => e.expConList));
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('รายจ่ายคงที่', style: MyTheme.textTheme.headline3),
        GridView.builder(
          physics: const ScrollPhysics(),
          shrinkWrap: true,
          itemCount: expConList.length,
          gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
            maxCrossAxisExtent: 100,
            mainAxisSpacing: 10,
            crossAxisSpacing: 10,
          ),
          itemBuilder: (_, index) {
            return Column(
              children: [
                Badge(
                  animationType: BadgeAnimationType.scale,
                  showBadge: expConList[index].flows.isEmpty ? false : true,
                  badgeContent: Text(
                    '${expConList[index].flows.length}',
                    style: const TextStyle(fontSize: 15),
                  ),
                  child: Column(
                    children: [
                      ElevatedButton(
                        onPressed: () {
                          ref.read(provDFlow).setColorBackground('expense');
                          ref.read(provDFlow).setCurrCat(expConList[index]);
                          AutoRouter.of(context).push(DailyFlowCreateRoute());
                        },
                        style: ElevatedButton.styleFrom(
                          elevation: 0.0,
                          shadowColor:
                              Colors.transparent, //remove shadow on button
                          primary: expConList[index].budgets.isEmpty
                              ? MyTheme.negativeMinor
                              : MyTheme.negativeMajor,
                          textStyle: const TextStyle(
                              fontSize: 30, fontWeight: FontWeight.bold),
                          padding: const EdgeInsets.symmetric(
                              horizontal: 15, vertical: 15),

                          shape: const CircleBorder(),
                        ),
                        child: Column(
                          //mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              HelperIcons.getIconData(expConList[index].icon),
                              color: Colors.white,
                            ),
                            if (expConList[index].flows.isNotEmpty) ...[
                              Text(
                                _loopFlow(expConList[index].flows),
                              ),
                            ],
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                Text(expConList[index].name)
              ],
            );
          },
        ),
      ],
    );
  }
}

class ExpNonConTab extends ConsumerWidget {
  const ExpNonConTab({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final expNonConList = ref.watch(provDFlow.select((e) => e.expInconList));

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('รายจ่ายไม่คงที่', style: MyTheme.textTheme.headline3),
        GridView.builder(
          physics: const ScrollPhysics(),
          shrinkWrap: true,
          itemCount: expNonConList.length,
          gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
            maxCrossAxisExtent: 100,
            mainAxisSpacing: 10,
            crossAxisSpacing: 10,
          ),
          itemBuilder: (_, index) {
            return Column(
              children: [
                Badge(
                  animationType: BadgeAnimationType.scale,
                  showBadge: expNonConList[index].flows.isEmpty ? false : true,
                  badgeContent: Text(
                    '${expNonConList[index].flows.length}',
                    style: const TextStyle(fontSize: 15),
                  ),
                  child: Column(
                    children: [
                      ElevatedButton(
                        onPressed: () {
                          ref.read(provDFlow).setColorBackground('expense');
                          ref.read(provDFlow).setCurrCat(expNonConList[index]);
                          AutoRouter.of(context).push(DailyFlowCreateRoute());
                        },
                        style: ElevatedButton.styleFrom(
                          elevation: 0.0,
                          shadowColor:
                              Colors.transparent, //remove shadow on button
                          primary: expNonConList[index].budgets.isEmpty
                              ? MyTheme.negativeMinor
                              : MyTheme.negativeMajor,
                          textStyle: const TextStyle(
                              fontSize: 30, fontWeight: FontWeight.bold),
                          padding: const EdgeInsets.symmetric(
                              horizontal: 15, vertical: 15),

                          shape: const CircleBorder(),
                        ),
                        child: Column(
                          //mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              HelperIcons.getIconData(
                                  expNonConList[index].icon),
                              color: Colors.white,
                            ),
                            if (expNonConList[index].flows.isNotEmpty) ...[
                              Text(
                                _loopFlow(expNonConList[index].flows),
                              ),
                            ],
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                Text(expNonConList[index].name)
              ],
            );
          },
        ),
      ],
    );
  }

  setCatType(int i) {}
}

String _loopFlow(List<DFlowFlow> flows) {
  double sum = 0;
  flows.forEach((e) {
    sum += e.value;
  });
  return sum.toString();
}
