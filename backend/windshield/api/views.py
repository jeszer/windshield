from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from . import serializers
from . import models
from user.models import Province, NewUser
from user.serializers import ProvinceSerializer
from rest_framework.filters import OrderingFilter
from datetime import datetime, timedelta
from pytz import timezone
from django.db.models import Exists, OuterRef, Q, F, Prefetch

DEFUALT_CAT = [
            ('เงินเดือน', 1, 'briefcase'),
            ('ค่าจ้าง', 1, 'hand-holding-usd'),
            ('ค่าล่วงเวลา', 1, 'business-time'),
            ('โบนัส', 1, 'briefcase'),
            ('ค่าคอมมิชชั่น', 1, 'comment-dollar'),
            ('กำไรจากธุรกิจ', 1, 'dollar-sign'),
            ('ดอกเบี้ย', 2, 'percentage'),
            ('เงินปันผล', 2, 'chart-line'),
            ('ค่าเช่า', 2, 'building'),
            ('ขายสินทรัพย์', 2, 'hand-holding-usd'),
            ('เงินรางวัล', 3, 'trophy'),
            ('ค่าเลี้ยงดู', 3, 'hand-holding-usd'),
            ('อาหาร/เครื่่องดื่ม', 4, 'utensils'),
            ('ภายในครัวเรือน', 4, 'house-user'),
            ('ความบันเทิง/ความสุขส่วนบุคคล', 4, 'music'),
            ('สาธารณูปโภค', 4, 'bolt'),
            ('ดูแลตัวเอง', 4, 'heart'),
            ('ค่าเดินทาง', 4, 'route'),
            ('รักษาพยาบาล', 4, 'hand-holding-medical'),
            ('ดูแลบุพการี', 4, 'user-friends'),
            ('ดูแลบุตร', 4, 'baby'),
            ('ภาษี', 4, 'donate'),
            ('ชำระหนี้', 4, 'hand-holding-usd'),
            ('เสี่ยงดวง', 4, 'dice'),
            ('กิจกรรมทางศาสนา ', 4, 'praying-hands'),
            ('เช่าบ้าน', 5, 'home'),
            ('หนี้ กยศ. กองทุน กยศ.', 5, 'graduation-cap'),
            ('ผ่อนรถ', 5, 'car'),
            ('ผ่อนสินค้า', 5, 'shopping-cart'),
            ('ผ่อนหนี้นอกระบบ', 5, 'comments-dollar'),
            ('ผ่อนสินเชื่อส่วนบุคคล', 5, 'comments-dollar'),
            ('ผ่อนหนี้สหกรณ์', 5, 'comments-dollar'),
            ('เบี้ยประกัน', 5, 'file-contract'),
            ('ประกันสังคม', 6, 'building'),
            ('กองทุนสำรองเลี้ยงชีพ', 6, 'coins'),
            ('กอนทุน กบข.', 6, 'coins'),
            ('สหกรณ์ออมทรัพย์', 6, 'comments-dollar'),
            ('เงินออม', 6, 'piggy-bank'),
            ('เงินลงทุน', 6, 'chart-line')
            ]

class Provinces(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer

class FinancialTypeList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.FinancialTypeSerializer
    
    def list(self, request):
        if request.user.uuid is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    def get_queryset(self):
        uuid = self.request.user.uuid
        queryset = models.FinancialType.objects.all()
        domain = self.request.query_params.get("domain", None)
        if domain is not None:
            queryset = queryset.filter(domain=domain)
        cat = models.Category.objects.filter(user_id=uuid, isDeleted=False)
        queryset = queryset.prefetch_related(
            Prefetch('categories', queryset=cat)
        )
        return queryset

class DailyFlow(generics.RetrieveUpdateDestroyAPIView):
    permissions_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.DailyFlowSerializer
    queryset = models.DailyFlow.objects.all()
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(self.object)
        data = serializer.data
        self.object.delete()
        return Response(data, status=status.HTTP_202_ACCEPTED)

class DailyListFlow(generics.ListCreateAPIView):
    permissions_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.DailyFlowSerializer
    
    def list(self, request):
        if request.user.uuid is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    def get_queryset(self):
        uuid = self.request.user.uuid
        dfsheet = self.request.query_params.get("df_id", None)
        if dfsheet is not None:
            queryset = models.DailyFlow.objects.filter(df_id=dfsheet)
        else:
            date = datetime.now(tz= timezone('Asia/Bangkok'))
            dfsheet = models.DailyFlowSheet.objects.get(owner_id = uuid, date=date)
            queryset = models.DailyFlow.objects.filter(df_id=dfsheet.id)
        return queryset
    
    def create(self, request):
        serializer = serializers.DailyFlowCreateSerializer(data=request.data, many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        n = len(request.data)
        if not isinstance(request.data, list): 
            df_id = request.data["df_id"]
            n = 1
        else: 
            df_id = request.data[0]["df_id"]
        results = models.DailyFlow.objects.filter(df_id=df_id)
        output_serializer = self.get_serializer(results, many=True)
        data = output_serializer.data[-n:]
        return Response(data)    

class DailyFlowSheet(generics.RetrieveAPIView):
    permissions_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.DailyFlowSheetSerializer
    
    def retrieve(self, request, pk=None):
        if request.user.uuid is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        queryset = models.DailyFlowSheet.objects.filter(owner_id=request.user.uuid)
        object = self.get_object()
        serializer = self.serializer_class(object, many=False)
        return Response(serializer.data)
    
    def get_object(self):
        uuid = self.request.user.uuid
        date = self.request.query_params.get("date", None)
        if date is None:
            date = datetime.now(tz= timezone('Asia/Bangkok'))
        try:
            dfsheet = models.DailyFlowSheet.objects.get(owner_id = uuid, date=date)
        except models.DailyFlowSheet.DoesNotExist:
            serializer = serializers.DailyFlowSheetCreateSerializer(data={"owner_id": uuid, "date":date})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            dfsheet = models.DailyFlowSheet.objects.get(owner_id = uuid, date=date)
        return dfsheet

class DailyFlowSheetList(generics.ListAPIView):
    permissions_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.DailyFlowSheetSerializer
    
    def list(self, request):
        if request.user.uuid is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    def get_queryset(self):
        uuid = self.request.user.uuid
        queryset = models.DailyFlowSheet.objects.filter(owner_id = uuid)
        start = self.request.query_params.get("start", None)
        if start is not None:
            start = datetime.strptime(start, "%Y-%m-%d")
            queryset = queryset.filter(date__gte=start)
        end = self.request.query_params.get("end", None)
        if end is not None:
            end = datetime.strptime(end, "%Y-%m-%d")
            queryset = queryset.filter(date__lte=end)
        return queryset

class Method(generics.ListCreateAPIView):
    permissions_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.MethodSerializer
    
    def list(self, request):
        if request.user.uuid is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    def get_queryset(self):
        uuid = self.request.user.uuid
        queryset = models.Method.objects.filter(Q(user_id=uuid) | Q(user_id=None))
        return queryset
    
    def create(self, request, *args, **kwargs):
        uuid = self.request.user.uuid
        if uuid is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return super().create(request, *args, **kwargs)
        
    def perform_create(self, serializer):
        uuid = self.request.user.uuid
        owner_instance = NewUser.objects.get(uuid=uuid)
        serializer.save(user_id=owner_instance, **self.request.data)
          
class Statement(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.StatementSerializer
    filter_backends = [OrderingFilter]
    # queryset = models.FinancialStatementPlan.objects.all()

    def list(self, request):
        if request.user.uuid is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        uuid = self.request.user.uuid
        queryset = models.FinancialStatementPlan.objects.filter(owner_id=uuid)
        lower = self.request.query_params.get("lower-date", None)
        upper = self.request.query_params.get("upper-date", None)
        date = self.request.query_params.get("date", None)
        if lower is not None:
            lower = datetime.strptime(lower, "%Y-%m-%d")
            queryset = queryset.filter(end__gte=lower)
        if upper is not None:
            upper = datetime.strptime(upper, "%Y-%m-%d")
            queryset = queryset.filter(start__lte=upper)
        if date is not None:
            date = datetime.strptime(date, "%Y-%m-%d")
            queryset = queryset.filter(start__lte=date, end__gte=date)
        queryset = queryset.prefetch_related(
            Prefetch('budgets', queryset=models.Budget.objects.filter(cat_id__isDeleted=False))
        )
        return queryset
    
    def __date_validation__(self, queryset, start, end):
        if isinstance(start, str): start = datetime.strptime(start, "%Y-%m-%d")
        if isinstance(end, str): end = datetime.strptime(end, "%Y-%m-%d")
        if start >= end: return False
        tmp = queryset.filter(start__lt=start, end__gt=start)
        if tmp.count() > 0: return False
        tmp = queryset.filter(start__lt=end, end__gt=end)
        if tmp.count() > 0: return False
        tmp = queryset.filter(start__gt=start, end__lt=end)
        if tmp.count() > 0: return False
        return True
    
    def create(self, request, *args, **kwargs):
        uuid = self.request.user.uuid
        if uuid is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.perform_create(serializer)
    
    def perform_create(self, serializer):
        uuid = self.request.user.uuid
        startDate = self.request.data['start']
        endDate = self.request.data['end']
        month = str(self.request.data.pop("month"))
        month_instance = models.Month.objects.get(id=month)
        owner_instance = NewUser.objects.get(uuid=uuid)
        # -yymmdd-id
        queryset = models.FinancialStatementPlan.objects.filter(owner_id=uuid)
        if not self.__date_validation__(queryset, startDate, endDate):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        plans = queryset.filter(start=startDate, end=endDate)
        if(plans.filter(chosen=True).count() > 0):
            self.request.data['chosen'] = False
        else:
            self.request.data['chosen'] = True
        last_plan = plans.last()
        if last_plan is None : plan_id = 0
        else: 
            plan_id = int(last_plan.id[-1:]) + 1
        serializer.save(
            id = 'FSP' + str(uuid)[:10] + '-' + str(startDate)[2:4] + str(startDate)[5:7] + str(startDate)[-2:] + '-' + str(plan_id)[-1:],
            owner_id = owner_instance,
            month = month_instance,
            **self.request.data
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
            
class StatementChangeName(generics.UpdateAPIView):
    permissions_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.StatementUpdateSerializer
    
    def list(self, request):
        if request.user.uuid is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    def get_queryset(self):
        uuid = self.request.user.uuid
        self.queryset = models.FinancialStatementPlan.objects.filter(owner_id=uuid)
        return self.queryset

class StatementInstance(generics.RetrieveUpdateDestroyAPIView):
    permissions_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.StatementUpdateSerializer
    
    def list(self, request):
        if request.user.uuid is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    def get_queryset(self):
        uuid = self.request.user.uuid
        self.queryset = models.FinancialStatementPlan.objects.filter(owner_id=uuid)
        return self.queryset
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        active_instance = self.get_object()
        queryset = self.get_queryset().filter(start=active_instance.start, end=active_instance.end)
        instance = []
        for obj in queryset:
            if obj.id == kwargs["pk"]:
                obj.chosen = True
            else:
                obj.chosen = False
            obj.save()
            instance.append(obj)
        serializer = self.get_serializer(instance, many=True, partial=partial)
        return Response(serializer.data)
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        print(self.object)
        if self.object.chosen:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(self.object)
        data = serializer.data
        self.object.delete()
        return Response(data, status=status.HTTP_202_ACCEPTED)

class Asset(generics.ListCreateAPIView):
    permissions_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.AssetsSerializer
    
    def list(self, request):
        if request.user.uuid is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    def get_queryset(self):
        uuid = self.request.user.uuid
        bsheet = models.BalanceSheet.objects.get(owner_id=uuid)
        queryset = models.Asset.objects.filter(bsheet_id=bsheet.id, cat_id__isDeleted=False)
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.perform_create(serializers.AssetSerializer)
    
    def perform_create(self, serializer):
        uuid = self.request.user.uuid
        if uuid is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        cat_id = self.request.data.pop("cat_id", None)
        bsheet = models.BalanceSheet.objects.get(owner_id=uuid)
        try:
            cat = models.Category.objects.get(id=cat_id)
        except models.Category.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        created_inst = models.Asset.objects.create(
                        bsheet_id = bsheet,
                        cat_id = cat,
                        **self.request.data
                        )
        data = serializer(created_inst).data
        return Response(data, status=status.HTTP_201_CREATED)

class AssetInstance(generics.RetrieveUpdateDestroyAPIView):
    permissions_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.AssetSerializer
    queryset = models.Asset.objects.all()
    
    def get_object(self):
        try:
            self.serializer_class = serializers.AssetsSerializer
            return models.Asset.objects.get(id=self.kwargs['pk'])
        except models.Asset.DoesNotExist:
            return None

class Debt(generics.ListCreateAPIView):
    permissions_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.DebtsSerializer

    def list(self, request):
        if request.user.uuid is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    def get_queryset(self):
        uuid = self.request.user.uuid
        bsheet = models.BalanceSheet.objects.get(owner_id=uuid)
        queryset = models.Debt.objects.filter(bsheet_id=bsheet.id, cat_id__isDeleted=False)
        priority = self.request.query_params.get("priority", False)
        if priority:
            queryset = queryset.order_by(
                F('interest').desc(nulls_last=True),
                F('balance').asc(),
                F('debt_term').asc(nulls_first=True)
            )
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.perform_create(serializers.DebtSerializer)
    
    def perform_create(self, serializer):
        uuid = self.request.user.uuid
        if uuid is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        cat_id = self.request.data.pop("cat_id", None)
        bsheet = models.BalanceSheet.objects.get(owner_id=uuid)
        try:
            cat = models.Category.objects.get(id=cat_id)
        except models.Category.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        created_inst = models.Debt.objects.create(
                        bsheet_id = bsheet,
                        cat_id = cat,
                        **self.request.data
                        )
        data = serializer(created_inst).data
        return Response(data, status=status.HTTP_201_CREATED)

class DebtInstance(generics.RetrieveUpdateDestroyAPIView):
    permissions_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.DebtSerializer
    queryset = models.Debt.objects.all()
    
    def get_object(self):
        try:
            self.serializer_class = serializers.DebtsSerializer
            return models.Debt.objects.get(id=self.kwargs['pk'])
        except models.Debt.DoesNotExist:
            return None
    
class BalanceSheet(generics.RetrieveAPIView):
    permissions_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.BalanceSheetSerializer
    
    def get_object(self):
        uuid = self.request.user.uuid
        if uuid is not None:
            try:
                assets = models.Asset.objects.filter(cat_id__isDeleted=False)
                debts = models.Debt.objects.filter(cat_id__isDeleted=False)
                bsheet = models.BalanceSheet.objects.prefetch_related(
                    Prefetch('assets', queryset=assets),
                    Prefetch('debts', queryset=debts)
                ).get(owner_id = uuid)
            except models.BalanceSheet.DoesNotExist:
                owner = models.NewUser.objects.get(uuid=uuid)
                bsheet = models.BalanceSheet.objects.create(id = "BSH" + str(uuid)[:10],
                                                   owner_id = owner)
        return bsheet

class CategoryWithBudgetsAndFlows(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.CategoryWithBudgetAndFlowsSerializer
    
    def list(self, request):
        if request.user.uuid is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    def get_queryset(self):
        uuid = self.request.user.uuid
        queryset = models.Category.objects.filter(user_id=uuid)
        date = self.request.query_params.get('date', None)
        if date is None:
            date = datetime.now(tz= timezone('Asia/Bangkok'))
        as_used = eval(self.request.query_params.get('as_used', 'False'))
        if as_used:
            queryset = queryset.filter(
                Exists(models.Asset.objects.filter(cat_id__id=OuterRef('pk'))) |
                Exists(models.Debt.objects.filter(cat_id__id=OuterRef('pk'))) |
                Q(ftype__domain__in=["INC", "EXP", "GOL"], isDeleted=False)
                )
        domain = self.request.query_params.getlist('domain')
        if len(domain) > 0:
            queryset = queryset.filter(ftype__domain__in=domain)
        try:
            fplan = models.FinancialStatementPlan.objects.get(chosen=True, start__lte=date, end__gte=date)
            fplan_id = fplan.id
        except models.FinancialStatementPlan.DoesNotExist:
            fplan_id = None
        budgets = models.Budget.objects.filter(fplan=fplan_id)
        try:
            dfsheet = models.DailyFlowSheet.objects.get(date=date)
            df_id = dfsheet.id
        except models.DailyFlowSheet.DoesNotExist:
            df_id = None
        flows = models.DailyFlow.objects.filter(df_id=df_id)
        queryset = queryset.prefetch_related(
            Prefetch('budgets', queryset=budgets)
        )
        queryset = queryset.prefetch_related(
            Prefetch('flows', queryset=flows)
        )
        return queryset

class DefaultCategories(generics.ListCreateAPIView):
    permissions_classes = [permissions.IsAdminUser]
    serializer_class = serializers.DefaultCategoriesSerializer
    queryset = models.DefaultCategory.objects.all()

class Category(generics.RetrieveUpdateAPIView):
    permissions_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.CategorySerializer
    
    def list(self, request):
        if request.user.uuid is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    def get_queryset(self):
        uuid = self.request.user.uuid
        queryset = models.Category.objects.filter(user_id=uuid)
        return queryset
        
class Categories(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.CategorySerializer

    def list(self, request):
        if request.user.uuid is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        uuid = self.request.user.uuid
        queryset = models.Category.objects.filter(user_id=uuid)
        if not queryset:
            owner = models.NewUser.objects.get(uuid=uuid)
            default_cat = models.DefaultCategory.objects.all()
            for cat in default_cat:
                models.Category.objects.create(name=cat.name, ftype=cat.ftype, user_id=owner, icon=cat.icon)
            queryset = models.Category.objects.filter(user_id=uuid)
        as_used = eval(self.request.query_params.get('as_used', "False"))
        if as_used:
            queryset = queryset.filter(
                Exists(models.Asset.objects.filter(cat_id__id=OuterRef('pk'))) |
                Exists(models.Debt.objects.filter(cat_id__id=OuterRef('pk'))) |
                Q(ftype__domain__in=["INC", "EXP", "GOL"], isDeleted=False)
                )
        domain = self.request.query_params.getlist('domain')
        if len(domain) > 0:
            queryset = queryset.filter(ftype__domain__in=domain)
        return queryset
    
    def perform_create(self, serializer):
        uuid = self.request.user.uuid
        owner = NewUser.objects.get(uuid=uuid)
        ftype = str(self.request.data.pop("ftype"))
        ftype_instance = models.FinancialType.objects.get(id=ftype)
        return serializer.save( 
                        user_id = owner,
                        ftype = ftype_instance,
                        **self.request.data
                        )
    
class Budget(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.BudgetCategorySerializer
    
    def list(self, request):
        if request.user.uuid is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    def get_queryset(self):
        fplan = self.request.query_params.get("fplan", None)
        fplan_queryset = models.FinancialStatementPlan.objects.filter(owner_id=self.request.user.uuid)
        if fplan is None:
            now = datetime.now(tz= timezone('Asia/Bangkok'))
            fplan_instance = fplan_queryset.get(start__lte=now, end__gte=now, chosen=True)
        else: 
            fplan_instance = fplan_queryset.get(id=fplan)
        queryset = models.Budget.objects.filter(fplan=fplan_instance, cat_id__isDeleted=False)
        return queryset
    
    def create(self, request):
        serializer = serializers.BudgetSerializer(data=request.data, many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        n = len(request.data)
        if not isinstance(request.data, list): 
            fplan = request.data["fplan"]
            n = 1
        else: 
            fplan = request.data[0]["fplan"]
        results = models.Budget.objects.filter(fplan=fplan)
        output_serializer = self.serializer_class(results, many=True)
        data = output_serializer.data[-n:]
        return Response(data)
    
class BudgetUpdate(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.BudgetUpdateSerializer
    queryset = models.Budget.objects.all()
    
    def get_object(self, obj_id):
        try:
            return models.Budget.objects.get(id=obj_id)
        except models.Budget.DoesNotExist:
            raise status.HTTP_400_BAD_REQUEST
    
    def validate_ids(self, id_list):
        for id in id_list:
            try:
                models.Budget.objects.get(id=id)
            except models.Budget.DoesNotExist:
                raise status.HTTP_400_BAD_REQUEST
        return True
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        if isinstance(request.data, list):
            budget_ids = [i['id'] for i in request.data]
            self.validate_ids(budget_ids)
            result = []
            for obj in request.data:
                budget_id = obj['id']
                inst = self.get_object(budget_id)
                inst.budget_per_period = obj['budget_per_period']
                inst.frequency = obj['frequency']
                inst.save()
                result.append(inst)
        else:
            result = self.get_object(request.data['id'])
            result.budget_per_period = request.data['budget_per_period']
            result.frequency = request.data['frequency']
            result.save()
        serializer = serializers.BudgetCategorySerializer(result, many=isinstance(request.data, list), partial=partial)
        return Response(serializer.data)
    
class BudgetDelete(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.BudgetDeleteSerializer
    queryset = models.Budget.objects.all()
    
    def delete(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            targets = models.Budget.objects.filter(id__in=request.data)
            result = targets.delete()
            return Response(result[0], status=status.HTTP_202_ACCEPTED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class FinancialGoalInstance(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.FinancialGoalsSerializer
    
    def list(self, request):
        if request.user.uuid is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    def get_queryset(self):
        uuid = self.request.user.uuid
        queryset = models.FinancialGoal.objects.filter(user_id=uuid)
        return queryset
    
class FinancialGoals(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.FinancialGoalsSerializer
    
    def list(self, request):
        if request.user.uuid is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    def get_queryset(self):
        uuid = self.request.user.uuid
        queryset = models.FinancialGoal.objects.filter(user_id=uuid)
        date = self.request.query_params.get("date", None)
        if date is not None:
            queryset = queryset.filter(start__lte=date)
        completed = self.request.query_params.get("completed", None)
        if completed is not None:
            completed = eval(completed)
            if completed:
                queryset = queryset.filter(total_progress__gte=F("goal"))
            else:
                queryset = queryset.filter(total_progress__lt=F("goal"))
        return queryset
    
    def perform_create(self, serializer):
        uuid = self.request.user.uuid
        owner = NewUser.objects.get(uuid=uuid)
        return serializer.save( 
                        user_id = owner,
                        **self.request.data
                        )
        
class FinancialStatus(APIView):
    permission_classes = [permissions.IsAuthenticated]
    past_days = 30
    
    def __balance_sheet__(self):
        try:
            bsheet = models.BalanceSheet.objects.get(owner_id=self.request.user.uuid)
            last_log = models.BalanceSheetLog.objects.filter(bsheet_id=bsheet.id).latest('timestamp')
        except (models.BalanceSheet.DoesNotExist, models.BalanceSheetLog.DoesNotExist):
            return None
        return {
            "asset": last_log.asset_value,
            "debt": last_log.debt_balance
            }
    
    def __cash_flow__(self):
        min_date = datetime.today() - timedelta(days=self.past_days)
        cash_flow = {
            "working inc": 0,
            "investment inc": 0,
            "other inc": 0,
            "inconsistance exp": 0,
            "consistance exp": 0,
            "other exp": 0,
            "debt exp": 0
            }
        try:
            data = models.DailyFlowSheet.objects.filter(owner_id = self.request.user.uuid, date__gt=min_date)
            dfsheets = serializers.DailyFlowSheetSerializer(data, many=True)
        except models.DailyFlowSheet.DoesNotExist:
            return None
        for sheet in dfsheets.data:
            for flow in sheet["flows"]:
                ftype = int(flow['category']['ftype'])
                cat_name = flow['category']['name']
                if ftype == 1:
                    cash_flow["working inc"] += float(flow['value'])
                elif ftype == 2:
                    cash_flow["investment inc"] += float(flow['value'])
                elif ftype == 3:
                    cash_flow["other inc"] += float(flow['value'])
                elif ftype == 4:
                    cash_flow["inconsistance exp"] += float(flow['value'])
                elif ftype == 5:
                    cash_flow["consistance exp"] += float(flow['value'])
                elif ftype == 6:
                    cash_flow["other exp"] += float(flow['value'])
                
                if ("ผ่อน" in cat_name or "หนี้" in cat_name) and (ftype == 4 or ftype == 5):
                    cash_flow["debt exp"] += float(flow["value"])
                elif ftype == 10 or ftype == 11:
                    cash_flow["debt exp"] += float(flow["value"])
        return cash_flow
    
    def __asset__(self):
        try:
            bsheet = models.BalanceSheet.objects.get(owner_id=self.request.user.uuid)
            data = models.Asset.objects.filter(bsheet_id=bsheet.id)
            assets = serializers.AssetsSerializer(data, many=True)
        except (models.BalanceSheet.DoesNotExist, models.Asset.DoesNotExist):
            return None
        asset = {
            "liquid ass": 0,
            "investment ass": 0,
            "personal ass": 0,
        }
        for inst in assets.data:
            ftype = int(inst["cat_id"]["ftype"])
            if ftype == 7:
                asset["liquid ass"] += float(inst["recent_value"])
            elif ftype == 8:
                asset["investment ass"] += float(inst["recent_value"])
            elif ftype == 9:
                asset["personal ass"] += float(inst["recent_value"])
        return asset
    
    def __debt__(self):
        try:
            bsheet = models.BalanceSheet.objects.get(owner_id=self.request.user.uuid)
            data = models.Debt.objects.filter(bsheet_id=bsheet.id)
            debts = serializers.DebtsSerializer(data, many=True)
        except (models.BalanceSheet.DoesNotExist, models.Debt.DoesNotExist):
            return None
        debt = {
            "short term": 0,
            "long term": 0
        }
        for inst in debts.data:
            ftype = int(inst["cat_id"]["ftype"])
            if ftype == 10:
                debt["short term"] += float(inst["balance"])
            elif ftype == 11:
                debt["long term"] += float(inst["balance"])
        return debt
    
    def __net_worth__(self, balance):
        if balance is not None: 
            return balance["asset"] - balance["debt"]
        return None
    
    def __net_cashflow__(self, cash_flow):
        if cash_flow is not None:
            income = cash_flow["working inc"] + cash_flow["investment inc"] + cash_flow["other inc"]
            expense = cash_flow["inconsistance exp"] + cash_flow["consistance exp"] + cash_flow["other exp"]
            if income != 0 or expense != 0:
                return income - expense
        return None
    
    def __survival_ratio__(self, cash_flow):
        if cash_flow is not None:
            expense = cash_flow["inconsistance exp"] + cash_flow["consistance exp"] + cash_flow["other exp"]
            if expense != 0:
                return (cash_flow["working inc"] + cash_flow["investment inc"]) / expense
        return None
    
    def __wealth_ratio__(self, cash_flow):
        if cash_flow is not None:
            expense = cash_flow["inconsistance exp"] + cash_flow["consistance exp"] + cash_flow["other exp"]
            if expense != 0:
                return cash_flow["investment inc"] / expense
        return None
    
    def __basic_liquidity_ratio__(self, cash_flow, asset):
        if cash_flow is not None and asset is not None:
            expense = cash_flow["inconsistance exp"] + cash_flow["consistance exp"] + cash_flow["other exp"]
            if expense != 0:
                return asset["liquid ass"] / expense
        return None
    
    def __debt_service_ratio__(self, cash_flow):
        if cash_flow is not None:
            income = cash_flow["working inc"] + cash_flow["investment inc"] + cash_flow["other inc"]
            if income != 0:
                return cash_flow['debt exp'] / income
        return None
    
    def __saving_ratio__(self, cash_flow):
        if cash_flow is not None:
            income = cash_flow["working inc"] + cash_flow["investment inc"] + cash_flow["other inc"]
            if income != 0:
                return cash_flow["other exp"] / income
        return None
    
    def __investment_ratio__(self, asset, balance):
        if balance is not None: 
            net_worth = self.__net_worth__(balance)
            if net_worth is not None and net_worth != 0:
                return asset["investment ass"] / net_worth
        return None
    
    def get(self, request):
        if self.request.user.uuid is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        self.past_days = int(request.query_params.get("days", 30))
        cash_flow = self.__cash_flow__()
        balance = self.__balance_sheet__()
        asset = self.__asset__()
        finstatus = {
            "Net Worth": self.__net_worth__(balance), 
            "Net Cashflow": self.__net_cashflow__(cash_flow),
            "Survival Ratio": self.__survival_ratio__(cash_flow),
            "Wealth Ratio": self.__wealth_ratio__(cash_flow),
            "Basic Liquidity Ratio": self.__basic_liquidity_ratio__(cash_flow, asset),
            "Debt Service Ratio": self.__debt_service_ratio__(cash_flow),
            "Saving Ratio": self.__saving_ratio__(cash_flow),
            "Investment Ratio": self.__investment_ratio__(asset, balance),
            "Financial Health": None
            } 
        return Response(finstatus)
    
    