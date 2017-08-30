# -*- coding: UTF-8 -*-
from rest_framework import serializers
from account.models import Account
from django.contrib.auth.models import User
from models import SuiteTree, TestSuite, SuiteReport


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username',)


class SuiteTreeSerializers(serializers.ModelSerializer):
    class Meta:
        model = SuiteTree
        fields = '__all__'


class AccountSerializers(serializers.ModelSerializer):
    user = UserSerializers(read_only=True)

    class Meta:
        model = Account
        fields = '__all__'


class TestSuiteSerializers(serializers.ModelSerializer):
    roots = SuiteTreeSerializers(many=True)

    class Meta:
        model = TestSuite
        fields = ('id', 'name', 'project', 'roots')

    def create(self, validated_data):
        roots = validated_data.pop('roots')
        test_suite = TestSuite.objects.create(**validated_data)
        for root in roots:
            tree = SuiteTree.objects.create(mid=root['mid'], parent=root['parent'], name=root['name'], key=root['key'],
                                            level=root['key'])
            test_suite.roots.add(tree)
        return test_suite


class TestSuiteName(serializers.ModelSerializer):
    class Meta:
        model = TestSuite
        fields = ('name',)


class SuiteReportSerializers(serializers.ModelSerializer):
    runner = AccountSerializers(read_only=True)
    suite = TestSuiteName(read_only=True)

    class Meta:
        model = SuiteReport
        fields = '__all__'

