from placebo_api.models import (Users, Drugstores, Drugs, Fda_drug_categories,
                                Support, Reviews, Ban, Blacklist)
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from .serializers import (
    ListUserSerializer, User_serializer, Drugstore_serializer,
    Drug_serializer, Support_serializer, Review_serializer
)
import datetime
# Create your views here.


# Class for User viewset
class UserViewSet(ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = ListUserSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action == "create":
            return User_serializer
        return self.serializer_class


# Class for Drugstore viewset
class DrugstoreViewSet(ModelViewSet):
    queryset = Drugstores.objects.all()
    serializer_class = Drugstore_serializer
    http_method_names = ['get', 'post', 'delete', 'patch', 'put']

    # def perform_create(self, serializer):
    #     print('here')
    #     return super().perform_create(serializer)


# Class for Drugs viewset
class DrugsViewSet(ModelViewSet):
    queryset = Drugs.objects.all()
    http_method_names = ['get', 'post', 'delete', 'patch', 'put']
    serializer_class = Drug_serializer

    # View drugs according to categories
    @action(methods=['GET'], detail=False, url_path=r'/drug/')
    def drugs_by_category(self, request):
        # Fetch the name of the category
        fda_name = Fda_drug_categories.objects.get('category_name')
        category_name = Fda_drug_categories.objects.filter(
            name=fda_name).first()
        # List the drugs that fall under that category
        name_of_category = Drugs.objects.filter(category=category_name).first()
        serializer = Drug_serializer(name_of_category, many=True).data
        return Response(serializer)

    # Find pharmacies selling a particular drug (pricing can come later)
    @action(methods=['GET'], detail=True, url_path=r'/stores/')
    def list_drugstore(self, request):
        drug = self.get_object()
        # Using the drug selected, fetch an array of pharmacies/drugstores
        # brand_name = Drugs.objects.filter(brand_name=)
        # price = Drugs.objects.get()
        if Drugs.objects.contains(drug):
            pharmacy = Drugs.objects.get(Drugs.prn)
            price = Drugs.objects.get(Drugs.pricing)
        serializer = Drugstore_serializer(pharmacy, price, many=True).data
        return Response(serializer)

    # View number of expired, banned, children, otc and total drugs
    # (Come back to this later)
    @action(methods=['GET'], detail=False, url_path=r'/pharm_details/')
    def Placebo_pharm_details(self, request):
        # all_drugs = Drugs.objects.all()
        today = datetime.datetime.now().date()
        drug = Drugs.objects.filter(Drugs.exp_date <= today)
        expired_count = len(drug)
        serializer = Drug_serializer(expired_count, many=True).data
        return Response(serializer)


# Class for Kids viewset
class KidsViewSet(ModelViewSet):
    queryset = Drugs.objects.filter(child_friendly=True)
    http_method_names = ['get', 'post', 'delete', 'patch', 'put']
    serializer_class = Drug_serializer


# Class for OTC viewset
class OTCViewSet(ModelViewSet):
    queryset = Drugs.objects.filter(otc=True)
    http_method_names = ['get', 'post', 'delete', 'patch', 'put']
    serializer_class = Drug_serializer


# Class for Support viewset
class SupportViewSet(ModelViewSet):
    queryset = Support.objects.all()
    http_method_names = ['get', 'post']
    serializer_class = Support_serializer

    # See a list of support tickets
    @action(methods=['GET'], detail=False, url_path='user/supportticket/')
    def send_supportmessage(self, request, phonenumber):
        # Fetch user support tickets
        user_tickets = Support.objects.filter(phonenumber=phonenumber).first()
        serializer = Support_serializer(user_tickets).data
        return Response(serializer)


# Class for Review viewset
class ReviewViewSet(ModelViewSet):
    queryset = Reviews.objects.all()
    http_method_names = ['get', 'post', 'delete']
    serializer_class = Review_serializer

    # See a user's reviews
    @action(methods=['GET'], detail=False, url_path='/user/reviews/')
    def user_review(self, request, phonenumber):
        # Fetch user reviews
        user_reviews = Reviews.objects.filter(phonenumber=phonenumber).first()
        serializer = Review_serializer(user_reviews).data
        return Response(serializer)


# Class for Ban viewset
class BanViewSet(ModelViewSet):
    queryset = Ban.objects.all()
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    serializer_class = Drug_serializer


# Class for Blacklist viewset
class BlacklistViewSet(ModelViewSet):
    queryset = Blacklist.objects.all()
    http_method_names = ['get', 'post', 'put', 'patch']
    serializer_class = Drugstore_serializer
