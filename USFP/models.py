from django.db import models


# Create your models here.


class ReDefinedManager(models.Manager):
    def get_queryset(self):
        return models.Manager.get_queryset(self).filter(isDelete=False)


class Area(models.Model):
    arID = models.AutoField(primary_key=True, )
    arName = models.CharField(max_length=10, null=False, blank=False)
    arStart = models.DateTimeField(auto_created=True, null=False, blank=False)
    isDelete = models.BooleanField(null=False, blank=False, default=False)
    deleteDate = models.DateTimeField(blank=True, null=True)
    object = ReDefinedManager()
    objects = models.Manager()

    class Meta:
        db_table = 'Area'

    def __str__(self):
        return u'Area:%s' % self.arName


class CommonUser(models.Model):
    cuID = models.AutoField(primary_key=True, )
    cuName = models.CharField(max_length=20, null=False, blank=False)
    cuEmail = models.EmailField(null=False)
    cuImage = models.ImageField(upload_to="user_image", null=False, blank=False)
    cuPassword = models.CharField(max_length=20, null=False, blank=False)
    isDelete = models.BooleanField(blank=False, null=False, default=False)
    deleteDate = models.DateTimeField(blank=True, null=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE,on_ipdate=models.CASCADE, null=False, blank=False, related_name="CommonUser")
    object = ReDefinedManager()
    objects = models.Manager()

    class Meta:
        db_table = 'CommonUser'

    def __str__(self):
        return u'CommonUser:%s' % self.cuID


class VerifiedUser(models.Model):
    isAdmin = models.BooleanField(null=False, blank=False, default=False)
    cu = models.ForeignKey(CommonUser, on_delete=models.CASCADE,on_ipdate=models.CASCADE, null=False, blank=False, related_name="VerifiedUser",
                           primary_key=True)
    area = models.ManyToManyField(Area, related_name="VerifiedUser")

    class Meta:
        db_table = 'VerifiedUser'

    def __str__(self):
        return u'VerifiedUser:%s' % self.cu.cuID


class Suggestion(models.Model):
    sID = models.AutoField(primary_key=True, )
    postTime = models.DateTimeField(auto_created=True, null=False, blank=False)
    modifyTime = models.DateTimeField(auto_now=True, null=False, blank=False)
    visible = models.BooleanField(blank=False, null=False, default=False)
    isDelete = models.BooleanField(null=False, blank=False, default=False)
    deleteDate = models.DateTimeField(blank=True, null=True)
    content = models.TextField(blank=False, null=False)

    class Meta:
        db_table = 'Suggestion'

    def __str__(self):
        return u'Suggestion:%s' % self.sID


class ReplySuggestion(models.Model):
    rs = models.ForeignKey(Suggestion, primary_key=True, related_name="Self",on_delete=models.CASCADE,on_ipdate=models.CASCADE, )
    s = models.ForeignKey(Suggestion, null=False, blank=False, related_name="ReplySuggestion",on_delete=models.CASCADE,on_ipdate=models.CASCADE, )
    vf = models.ForeignKey(VerifiedUser, null=False, blank=False, related_name="ReplySuggestion",on_delete=models.CASCADE,on_ipdate=models.CASCADE, )

    class Meta:
        db_table = 'ReplySuggestion'

    def __str__(self):
        return u'ReplySuggestion:%s' % self.rs.sID


class UserOperation(models.Model):
    uoID = models.AutoField(primary_key=True, )
    user = models.ForeignKey(CommonUser, null=False, blank=False, related_name="UserOperation",on_delete=models.CASCADE,on_ipdate=models.CASCADE, )
    oType = models.CharField(max_length=10, choices=((1, 'delUser'), (2, 'upUser')))
    oTakeDate = models.DateTimeField(auto_created=True, null=False, blank=False)
    content = models.TextField(blank=False, null=False)
    vu = models.ForeignKey(VerifiedUser, null=False, blank=False,on_delete=models.CASCADE,on_ipdate=models.CASCADE, )

    class Meta:
        db_table = 'ReplySuggestion'

    def __str__(self):
        return u'ReplySuggestion:%s' % self.uoID


class AreaOperation(models.Model):
    aoID = models.AutoField(primary_key=True, )
    area = models.ForeignKey(Area, null=False, blank=False, related_name="UserOperation",on_delete=models.CASCADE,
                             on_ipdate=models.CASCADE, )
    aoType = models.CharField(max_length=10, choices=((1, 'delArea'), (2, 'upArea')))
    oTakeDate = models.DateTimeField(auto_created=True, null=False, blank=False)
    content = models.TextField(blank=False, null=False)
    vu = models.ForeignKey(VerifiedUser, null=False, blank=False,on_delete=models.CASCADE,on_ipdate=models.CASCADE, )

    class Meta:
        db_table = 'ReplySuggestion'

    def __str__(self):
        return u'ReplySuggestion:%s' % self.aoID
