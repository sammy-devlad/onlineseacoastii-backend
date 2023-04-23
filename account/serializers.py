from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from baseapp import utils


User = get_user_model()


class UpdateProfileImgSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["profile_image"]


class ProfileSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "full_name",
            "id",
            "password",
            "last_login",
            "is_superuser",
            "username",
            "is_staff",
            "is_active",
            "date_joined",
            "email",
            "balance",
            "first_name",
            "last_name",
            "phone_number",
            "date_of_birth",
            "gender",
            "next_of_kin",
            "address",
            "city",
            "state",
            "zipcode",
            "country",
            "account_type",
            "security_pin",
            "is_verified",
            "image_url",
        ]

    def get_image_url(self, obj):
        return obj.image_url()

    def get_full_name(self, obj):
        return obj.get_fullname()


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="A User with this Email already exist",
            )
        ],
    )

    password = serializers.CharField(
        write_only=False, required=True, validators=[validate_password]
    )

    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["email", "password", "confirm_password"]

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.pop("confirm_password", None)
        if password != confirm_password:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs


class CreateAcctSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "date_of_birth",
            "gender",
            "next_of_kin",
            "address",
            "city",
            "state",
            "zipcode",
            "country",
            "account_type",
            "security_pin",
            "password",
        ]
        extra_kwargs = {
            "username": {"required": False},
        }

    def save(self):
        account = User(
            email=self.validated_data["email"],
            first_name=self.validated_data["first_name"],
            last_name=self.validated_data["last_name"],
            phone_number=self.validated_data["phone_number"],
            date_of_birth=self.validated_data["date_of_birth"],
            gender=self.validated_data["gender"],
            next_of_kin=self.validated_data["next_of_kin"],
            address=self.validated_data["address"],
            city=self.validated_data["city"],
            state=self.validated_data["state"],
            zipcode=self.validated_data["zipcode"],
            country=self.validated_data["country"],
            account_type=self.validated_data["account_type"],
            security_pin=self.validated_data["security_pin"],
            username=utils.gen_random_number(),
        )
        password = self.validated_data["password"]
        account.set_password(password)

        account.save()
        return account
