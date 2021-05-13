from django.db import models


# Create your models here.


class ReDefinedManager(models.Manager):
    def get_queryset(self):
        return models.Manager.get_queryset(self).filter(isDelete=False)


class Area(models.Model):
    areaID = models.AutoField(primary_key=True, )
    areaName = models.CharField(max_length=10, null=False, blank=False, unique=True)
    areaStart = models.DateTimeField(auto_created=True, null=False, blank=False)
    isDelete = models.BooleanField(null=False, blank=False, default=False)
    deleteDate = models.DateTimeField(blank=True, null=True)
    object = ReDefinedManager()
    objects = models.Manager()

    class Meta:
        db_table = 'Area'

    def __str__(self):
        return u'Area:%s' % self.areaName


class CommonUser(models.Model):
    commonUserID = models.AutoField(primary_key=True, )
    commonUserName = models.CharField(max_length=20, null=False, blank=False)
    commonUserEmail = models.EmailField(null=False)
    commonUserImage = models.ImageField(upload_to="userImage", null=False, blank=False)
    commonUserPassword = models.CharField(max_length=20, null=False, blank=False)
    isDelete = models.BooleanField(blank=False, null=False, default=False)
    deleteDate = models.DateTimeField(blank=True, null=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, on_update=models.CASCADE, null=False, blank=False,
                             related_name="CommonUser")
    object = ReDefinedManager()
    objects = models.Manager()

    class Meta:
        db_table = 'CommonUser'

    def __str__(self):
        return u'CommonUser:%s' % self.commonUserID

    def isVerified(self):
        try:
            self.VerifiedUser
            return True
        except:
            return False


class VerifiedUser(models.Model):
    isAdmin = models.BooleanField(null=False, blank=False, default=False)
    commonUser = models.OneToOneField(CommonUser, on_delete=models.CASCADE, on_update=models.CASCADE, null=False,
                                      blank=False,
                                      related_name="VerifiedUser",
                                      primary_key=True)
    adminArea = models.ManyToManyField(Area, related_name="VerifiedUser")

    class Meta:
        db_table = 'VerifiedUser'

    def __str__(self):
        return u'VerifiedUser:%s' % self.commonUser.commonUserID


class Suggestion(models.Model):
    suggesionID = models.AutoField(primary_key=True, )
    postTime = models.DateTimeField(auto_created=True, null=False, blank=False)
    modifyTime = models.DateTimeField(auto_now=True, null=False, blank=False)
    visible = models.BooleanField(blank=False, null=False, default=False)
    isDelete = models.BooleanField(null=False, blank=False, default=False)
    deleteDate = models.DateTimeField(blank=True, null=True)
    content = models.TextField(blank=False, null=False)
    commonUser = models.ForeignKey(CommonUser, null=False, blank=False, related_name="Suggestion",
                                     on_delete=models.CASCADE, on_update=models.CASCADE, )
    object = ReDefinedManager()
    objects = models.Manager()

    class Meta:
        db_table = 'Suggestion'

    def __str__(self):
        return u'Suggestion:%s' % self.suggesionID

    def isReplied(self):
        try:
            self.ReplySuggestion
            return True
        except:
            return False


class ReplySuggestion(models.Model):
    replySuggestion = models.ForeignKey(Suggestion, primary_key=True, related_name="Self", on_delete=models.CASCADE,
                                        on_update=models.CASCADE, )
    suggestion = models.ForeignKey(Suggestion, null=False, blank=False, related_name="ReplySuggestion",
                                   on_delete=models.CASCADE,on_update=models.CASCADE, )

    class Meta:
        db_table = 'ReplySuggestion'

    def __str__(self):
        return u'ReplySuggestion:%s' % self.replySuggestion.suggesionID


class UserOperation(models.Model):
    userOperationID = models.AutoField(primary_key=True, )
    commonUser = models.ForeignKey(CommonUser, null=False, blank=False, related_name="UserOperation",
                                   on_delete=models.CASCADE, on_update=models.CASCADE, )
    operationType = models.CharField(max_length=10, choices=((1, 'delUser'), (2, 'upUser')))
    operationTakeDate = models.DateTimeField(auto_created=True, null=False, blank=False)
    content = models.TextField(blank=False, null=False)
    verifiedUser = models.ForeignKey(VerifiedUser, null=False, blank=False, on_delete=models.CASCADE,
                                     on_update=models.CASCADE, )

    class Meta:
        db_table = 'UserOperation'

    def __str__(self):
        return u'UserOperation:%s' % self.userOperationID


class AreaOperation(models.Model):
    areaOperaionID = models.AutoField(primary_key=True, )
    area = models.ForeignKey(Area, null=False, blank=False, related_name="AreaOperation", on_delete=models.CASCADE,
                             on_update=models.CASCADE, )
    opearionType = models.CharField(max_length=10, choices=((1, 'delArea'), (2, 'upArea')))
    opearionTakeDate = models.DateTimeField(auto_created=True, null=False, blank=False)
    content = models.TextField(blank=False, null=False)
    verifiedUser = models.ForeignKey(VerifiedUser, null=False, blank=False, on_delete=models.CASCADE,
                                     on_update=models.CASCADE, )

    class Meta:
        db_table = 'AreaOperation'

    def __str__(self):
        return u'AreaOperation:%s' % self.areaOperaionID


class SuggestionOperation(models.Model):
    suggestionOperaionID = models.AutoField(primary_key=True, )
    suggestion = models.ForeignKey(Suggestion, null=False, blank=False, related_name="SuggestionOperation",
                                   on_delete=models.CASCADE,on_update=models.CASCADE, )
    opearionType = models.CharField(max_length=10, choices=((1, 'delSuggestion'), (2, 'upSuggestion')))
    opearionTakeDate = models.DateTimeField(auto_created=True, null=False, blank=False)
    content = models.TextField(blank=False, null=False)
    verifiedUser = models.ForeignKey(VerifiedUser, null=False, blank=False, on_delete=models.CASCADE,
                                     on_update=models.CASCADE, )

    class Meta:
        db_table = 'SuggestionOperation'

    def __str__(self):
        return u'SuggestionOperation:%s' % self.suggestionOperaionID
