from django.db import transaction
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import (
    Contact, Users, Drugstores, Drugs, Support, Reviews, Ban, Blacklist,
    Medical_info, Fda_drug_categories)
# from profanity_check import predict
import datetime


class ListUserSerializer(ModelSerializer):
    """ Lists the users """
    age = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = "__all__"

    @staticmethod
    def get_age(obj):
        age = obj.age()
        return age


class User_serializer(ModelSerializer):
    """Serializer for UserViewSet"""
    countrycode = serializers.IntegerField(required=True)
    phone = serializers.IntegerField(required=True)
    allergies = serializers.CharField()
    medical_history = serializers.CharField()
    # attachments = serializers.FileField(upload_to='medical_history/')
    current_diagnosis = serializers.CharField()

    class Meta:
        model = Users
        fields = ['id', 'created_at', 'updated_at', 'avatar', 'firstname',
                  'lastname', 'countrycode', 'phone', 'email',  # 'attachments'
                  'reward_points', 'medical_history', 'other_health_info',
                  'dob', 'age', 'allergies', 'current_diagnosis']

    def validate(self, attrs):
        user_dob = attrs.get('dob')
        # To confirm that user is above 18 years old i.e. a legal adult
        current_date = datetime.datetime.now().date()
        # Convert datetime objects to string and then to integer
        strfuser_dob = user_dob.strftime("%Y")
        strfcurrent_date = current_date.strftime("%Y")
        fuser_dob = int(strfuser_dob)
        fcurrent_date = int(strfcurrent_date)
        user_age = fcurrent_date - fuser_dob
        # To confirm that an email or phone number has not been used before
        email = attrs.get('email')
        firstname = attrs.get('firstname')
        lastname = attrs.get('lastname')
        phone = attrs.get('phone')
        # phone = attrs.get('phone')

        if user_age < 18:
            raise serializers.ValidationError(
                {'Error': 'Only individuals above 18 can use this software.'})
        if Users.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {'Error': 'Email already exists.'})
        if Users.objects.filter(firstname=firstname):
            if Users.objects.filter(lastname=lastname).exists():
                raise serializers.ValidationError(
                    {'Error': 'User already exists'})
        if Contact.objects.filter(phone=phone).exists():
            raise serializers.ValidationError(
                {'Error': 'Phone number already exists'})

        return attrs

    @transaction.atomic
    # This decorator works like a bank transfer, such that it can only be
    # successful when all conditions are met
    def create(self, validated_user):
        id = validated_user.get('id')
        created_at = validated_user.get('created_at')
        avatar = validated_user.get('avatar')
        firstname = validated_user.get('firstname')
        lastname = validated_user.get('lastname')
        phone = validated_user.get('phone')
        countrycode = validated_user.get('countrycode')
        email = validated_user.get('email')
        reward_points = validated_user.get('reward_points')
        medical_history = validated_user.get('medical_history')
        # attachments = validated_user.get('attachments')
        allergies = validated_user.get('allergies')
        current_diagnosis = validated_user.get('current_diagnosis')
        other_health_info = validated_user.get('other_health_info')
        dob = validated_user.get('dob')

        user_phone = Contact.objects.create(
            countrycode=countrycode, phone=phone)
        user_med_history = Medical_info.objects.create(
            medical_history=medical_history,  # attachments=attachments,
            allergies=allergies, current_diagnosis=current_diagnosis)
        user = Users.objects.create(
            id=id, created_at=created_at, avatar=avatar, firstname=firstname,
            lastname=lastname, phonenumber=user_phone, email=email, dob=dob,
            reward_points=reward_points, medical_info=user_med_history,
            other_health_info=other_health_info)
        # Calculate user age as soon as each profile is created
        # user.age = user.calc_age()
        user.save()

        return validated_user

    def update(self, instance, validated_user):
        updated_at = validated_user.get('updated_at')
        avatar = validated_user.get('avatar')
        medical_history = validated_user.get('medical_history')
        # attachments = validated_user.get('attachments')
        allergies = validated_user.get('allergies')
        current_diagnosis = validated_user.get('current_diagnosis')
        other_health_info = validated_user.get('other_health_info')
        age = validated_user.get('age')

        user_med_history = Medical_info.objects.update(
            medical_history=medical_history,  # attachments=attachments,
            allergies=allergies, current_diagnosis=current_diagnosis)
        Users.objects.update(
            avatar=avatar, medical_info=user_med_history, age=age,
            other_health_info=other_health_info, updated_at=updated_at)

        return super().update(instance, validated_user)


class Drugstore_serializer(ModelSerializer):
    """Serializer for DrugstoreViewSet"""
    countrycode = serializers.IntegerField(read_only=True)
    phone = serializers.IntegerField(read_only=True)
# prn = serializers.PrimaryKeyRelatedField(queryset=Drugstores.objects.all())

    class Meta:
        model = Drugstores
        fields = ['id', 'prn', 'created_at', 'updated_at', 'name', 'image',
                  'location', 'email', 'phone', 'countrycode', 'logo',
                  'website', 'phar_license', 'owner_name', 'door_delivery',
                  'license_expdate', 'lead_pharmacist']
        read_only_fields = ('image', 'logo', 'phar_license')

        def validate(self, attrs):
            print("Inside validate")
            phar_license = attrs.get('phar_license_status')
            expiry_date = attrs.get('license_expdate')
            expiry_year = datetime.datetime.year(expiry_date)
            current_year = datetime.datetime.year()
            prn = attrs.get('prn')
            if Blacklist.objects.filter(prn=prn).exists():
                raise serializers.ValidationError({
                    'Error': 'This pharmacy has been blacklisted by the PCN'})
            if Drugstores.objects.filter(prn=prn).exists():
                raise serializers.ValidationError({
                    'Error':
                    'This pharmacy already exists on the Placebo database'})
            if phar_license.choices != 'PRESENT':
                raise serializers.ValidationError({
                    'Error': 'Please enter a valid license.'})
            if expiry_year < current_year:
                raise serializers.ValidationError(
                    {'Error':
                      'Please enter a valid license.This license is expired.'})

            return attrs

        @transaction.atomic
        def create(self, validated_drugstore):
            print(validated_drugstore)
            # id = validated_drugstore.get('id')
            prn = validated_drugstore.get('prn')
            # created_at = validated_drugstore.get('created_at')
            # name = re.match(r"^[A-Za-z0-9 ]+$")
            # To allow the user enter spaces between word inputs e.g. Blue Wave
            name = validated_drugstore.get('name').split()
            logo = validated_drugstore.get('logo')
            image = validated_drugstore.get('image')
            location = validated_drugstore.get('location')
            phone = validated_drugstore.get('phone')
            countrycode = validated_drugstore.get('countrycode')

            email = validated_drugstore.get('email')
            website = validated_drugstore.get('website')
            phar_license = validated_drugstore.get('phar_license')
            door_delivery = validated_drugstore.get('door_delivery')
            license_expdate = validated_drugstore.get('license_expdate')
            # owner_image = validated_drugstore.get('owner_image')
            owner_name = validated_drugstore.get('owner_name')
            lead_pharmacist = validated_drugstore.get('lead_pharmacist')
            # lead_pharmacist_image =
            # validated_drugstore.get('lead_pharmacist_image')

            pharm_phone = Contact.objects.create(
                phone=phone, countrycode=countrycode)
            other_contact_phone = Contact.objects.create(
                phone=phone, countrycode=countrycode)

            # Save the datafields

            drugstore = Drugstores.objects.create(
                name=name, image=image, prn=prn,
                location=location, owner_name=owner_name, email=email,
                phonenumber=pharm_phone, website=website, logo=logo,
                door_delivery=door_delivery, other_contact=other_contact_phone,
                phar_license=phar_license, license_expdate=license_expdate,
                lead_pharmacist=lead_pharmacist)
            
            drugstore.save()

            return validated_drugstore
            # return drug_store

        def update(self, instance, validated_drugstore):
            name = validated_drugstore.get('name').split()
            updated_at = validated_drugstore.get('updated_at')
            image = validated_drugstore.get('image')
            location = validated_drugstore.get('location')
            countrycode = validated_drugstore.get('countrycode')
            phone = validated_drugstore.get('phone')
            phar_license = validated_drugstore.get('phar_license')
            door_delivery = validated_drugstore.get('door_delivery')
            license_expdate = validated_drugstore.get('license_expdate')
            owner_name = validated_drugstore.get('owner_name')
            lead_pharmacist = validated_drugstore.get('lead_pharmacist')

            other_contacts_phone = Contact.objects.create(
                phone=phone, countrycode=countrycode)

            updatedrugstore = Drugstores.objects.update(
                name=name, updated_at=updated_at, image=image,
                owner_name=owner_name, location=location,
                other_contact=other_contacts_phone, phar_license=phar_license,
                door_delivery=door_delivery, license_expdate=license_expdate,
                lead_pharmacist=lead_pharmacist)
            
            updatedrugstore.save()

            return super().update(instance, validated_drugstore)


class Drug_serializer(ModelSerializer):
    name = serializers.CharField(required=True)
    drug_info = serializers.CharField(required=True)

    class Meta:
        model = Drugs
        fields = [
            'id', 'prn', 'created_at', 'updated_at', 'image', 'name',
            'drug_info', 'brand_name', 'product_desc', 'purpose',
            'contraindications', 'side_effects', 'nafdac_number', 'origin',
            'son_approved', 'upi', 'min_unitofpurchase', 'active_ingredients',
            'inactive_ingredients', 'uses', 'otc', 'pricing', 'child_friendly',
            'batch_num', 'man_date', 'exp_date', 'total_units', 'units_sold']

    def validate(self, attrs):
        source = attrs.getrc('origin')
        drug_man_date = attrs.get('man_date')
        drug_exp_date = attrs.get('exp_date')
        today_date = datetime.datetime.date()
        son_approved = attrs.get('son_approved')
        upi = attrs.get('upi')
        upi_obj = Ban.objects.filter(upi=upi).first()
        total_units = attrs.get('total_units')
        units_sold = attrs.get('units_sold')
        # prn_obj = Drugs.objects.filter(prn=prn).first()
        units_left = total_units - units_sold

        if Ban.objects.contains(upi_obj):
            raise serializers.ValidationError({
                'Error':
                'This drug is banned and cannot be sold on this platform'
                })
        if source.choices == 'IMPORTED':
            if son_approved == 'False':
                raise serializers.ValidationError(
                    {'Error': 'This drug does not have SON approval'})
        if drug_man_date >= today_date:
            raise serializers.ValidationError(
                {'Date Error': 'Date for drug manufacture is invalid'})
        if drug_exp_date <= today_date:
            raise serializers.ValidationError(
                {'Date Error': 'Drug is already expired'})
        if units_left == 0:
            raise serializers.ValidationError(
                {'Error': 'Drug is out of stock'})
        if units_left < 0:
            raise serializers.ValidationError(
                {'Error': 'There are only {units_left} left'})

        return attrs

    @transaction.atomic
    def create(self, validated_drug):
        id = validated_drug.get('id')
        upi = validated_drug.get('upi')
        prn = validated_drug.get('prn')
        created_at = validated_drug.get('created_at')
        image = validated_drug.get('image')
        name = validated_drug.get('name')
        drug_info = validated_drug.get('drug_info')
        brand_name = validated_drug.get('brand_name')
        product_desc = validated_drug.get('product_desc')
        purpose = validated_drug.get('purpose')
        contraindications = validated_drug.get('contraindications')
        side_effects = validated_drug.get('side_effects')
        nafdac_number = validated_drug.get('nafdac_number')
        origin = validated_drug.get('origin')
        son_approved = validated_drug.get('son_approved')
        min_unitofpurchase = validated_drug.get('min_unitofpurchase')
        active_ingredients = validated_drug.get('active_ingredients')
        inactive_ingredients = validated_drug.get('inactive_ingredients')
        uses = validated_drug.get('uses')
        otc = validated_drug.get('otc')
        pricing = validated_drug.get('pricing')
        child_friendly = validated_drug.get('child_friendly')
        batch_num = validated_drug.get('batch_num')
        man_date = validated_drug.get('man_date')
        exp_date = validated_drug.get('exp_date')
        total_units = validated_drug.get('total_units')
        units_sold = validated_drug.get('units_sold')

        drug_category = Fda_drug_categories.objects.create(
            name=name, drug_info=drug_info)

        Drugs.objects.create(
            id=id, upi=upi, created_at=created_at, image=image,
            brand_name=brand_name, origin=origin, otc=otc, man_date=man_date,
            product_desc=product_desc, purpose=purpose, pricing=pricing,
            contraindications=contraindications, side_effects=side_effects,
            nafdac_number=nafdac_number, son_approved=son_approved, uses=uses,
            min_unitofpurchase=min_unitofpurchase, batch_num=batch_num,
            active_ingredients=active_ingredients, category=drug_category,
            child_friendly=child_friendly, exp_date=exp_date,
            inactive_ingredients=inactive_ingredients, total_units=total_units,
            units_sold=units_sold, prn=prn)

        return validated_drug

    def update(self, instance, validated_drug):
        updated_at = validated_drug.get('updated_at')
        image = validated_drug.get('name')
        name = validated_drug.get('name')
        drug_info = validated_drug.get('drug_info')
        product_desc = validated_drug.get('product_desc')
        purpose = validated_drug.get('purpose')
        contraindications = validated_drug.get('contraindications')
        side_effects = validated_drug.get('side_effects')
        origin = validated_drug.get('origin')
        son_approved = validated_drug.get('son_approved')
        min_unitofpurchase = validated_drug.get('min_unitofpurchase')
        uses = validated_drug.get('uses')
        otc = validated_drug.get('otc')
        pricing = validated_drug.get('pricing')
        child_friendly = validated_drug.get('child_friendly')
        batch_num = validated_drug.get('batch_num')
        man_date = validated_drug.get('man_date')
        exp_date = validated_drug.get('exp_date')
        total_units = validated_drug.get('total_units')
        units_sold = validated_drug.get('units_sold')

        drug_category = Fda_drug_categories.objects.update(
            name=name, drug_info=drug_info)

        Drugs.objects.update(
            updated_at=updated_at, image=image, category=drug_category,
            product_desc=product_desc, purpose=purpose, origin=origin,
            uses=uses, otc=otc, contraindications=contraindications,
            side_effects=side_effects, son_approved=son_approved,
            min_unitofpurchase=min_unitofpurchase, pricing=pricing,
            batch_num=batch_num, child_friendly=child_friendly,
            man_date=man_date, exp_date=exp_date, total_units=total_units,
            units_sold=units_sold)

        return super().update(instance, validated_drug)


class Support_serializer(ModelSerializer):
    class Meta:
        model = Support
        fields = [
            'id', 'created_at', 'firstname', 'lastname',
            'phonenumber', 'email', 'message']

    def validate(self, attrs):
        ...
        # support_ticket = attrs.get('message')
        # if predict(support_ticket) == 1:
        #     raise serializers.ValidationError(
        #         {'Error': 'The use of profanities is not allowed'})

    @transaction.atomic
    def create(self, validated_message):
        id = validated_message.get('id')
        created_at = validated_message.get('created_at')
        firstname = validated_message.get('firstname')
        lastname = validated_message.get('lastname')
        phonenumber = validated_message.get('phonenumber')
        email = validated_message.get('email')
        message = validated_message.get('message')

        Support.objects.create(
            id=id, created_at=created_at, firstname=firstname,
            lastname=lastname, phonenumber=phonenumber, email=email,
            message=message)

        return validated_message


class Review_serializer(ModelSerializer):
    class Meta:
        model = Reviews
        fields = ['id', 'created_at', 'firstname',
                  'lastname', 'phonenumber', 'email', 'message']

    def validate(self, attrs):
        ...
        # user_review = attrs.get('message')
        # if predict(user_review) == 1:
        #     raise serializers.ValidationError(
        #         {'Error': 'The use of profanities is not allowed'})

    @transaction.atomic
    def create(self, validated_review):
        id = validated_review.get('id')
        created_at = validated_review.get('created_at')
        firstname = validated_review.get('firstname')
        lastname = validated_review.get('lastname')
        phonenumber = validated_review.get('phonenumber')
        email = validated_review.get('email')
        message = validated_review.get('message')

        Reviews.objects.create(
            id=id, created_at=created_at, firstname=firstname, email=email,
            lastname=lastname, phonenumber=phonenumber, message=message)

        return validated_review
