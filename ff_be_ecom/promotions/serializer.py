from rest_framework import serializers
from .models import Promotion
from pricing_rules.models import PricingRule
from pricing_rules.serializer import PricingRuleSerializer

class PromotionSerializer(serializers.ModelSerializer):
    rule = PricingRuleSerializer(read_only=True)
    rule_id = serializers.PrimaryKeyRelatedField(queryset=PricingRule.objects.all(), source='rule', write_only=True)
    class Meta:
        model = Promotion
        fields = ['id','code','name','description','rule','rule_id','active','usage_limit','used_count']