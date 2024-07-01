from mycloud import serializers


def patchValidator(data):
        if 'id' not in data:
            raise serializers.ValidationError({
                'message': 'no id parameter provided',
            })

        if 'comment' not in data:
            raise serializers.ValidationError({
                'message': 'no comment parameter provided',
            })
        
        return data
