
# from decimal import Decimal
from database import Base
from sqlalchemy import Table, MetaData, Column, Integer, ForeignKey, BigInteger, column, Computed
from sqlalchemy.orm import relationship
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import DateTime
from sqlalchemy import Time
from sqlalchemy import Boolean
from sqlalchemy import Double
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import Text
from sqlalchemy import DECIMAL
from sqlalchemy import JSON
from typing import Optional


class Infra(Base):
    __tablename__ = "infra"
    InfraId = Column(Integer(),
        primary_key=True,
        autoincrement=True,
    )
    InfraName = Column(String)
    InfraCategory = Column(String)
    TotalUnits = Column(String)
    AvailableUnits = Column(Integer)
    SoldUnits = Column(Integer)
    BookedUnits = Column(Integer)
    InfraFloorCount = Column(Integer)
    CreatedDate = Column(DateTime)
    UpdatedDate = Column(DateTime)
    SiteId = Column(Integer, ForeignKey("site.SiteId"))
    CreatedById = Column(Integer, ForeignKey("users.id"))
    users = relationship("Users")
    site = relationship("Site")


class Site(Base):
    __tablename__ = "site"
    SiteId = Column(Integer(),
        primary_key=True,
        autoincrement=True,
    )
    SiteName = Column(String, unique=True)
    SiteTypeId = Column(Integer, ForeignKey("sitetype.SiteTypeId"))
    sitetype = relationship("SiteType")
    SiteCity = Column(String)
    SiteAddress = Column(String)
    SiteStatus = Column(String)
    SiteSizeSqFt = Column(Float)
    OperationalDate = Column(DateTime)
    IsOperational = Column(Boolean)
    DeveloperId = Column(Integer, ForeignKey("Developer.DeveloperId"))
    developer = relationship("Developer")
    SiteDescription = Column(String)
    NearbyLandmarks = Column(String)
    CreatedDate = Column(DateTime)
    UpdateDate = Column(DateTime)
    # CreatedById = Column(Integer)
    CreatedById = Column(Integer, ForeignKey("users.id"))
    created_by = relationship("Users")
    IsDeleted = Column(Integer, default=0)


class SiteInfra(Base):
    __tablename__ = "SiteInfra"
    SiteInfraId = Column(Integer(),
        primary_key=True,
        autoincrement=True,
    )
    SiteId = Column(Integer)
    InfraId = Column(Integer)
    InfraUnitId = Column(Integer)
    InfraType = Column(Integer)
    Active = Column(Boolean)
    CreatedDate = Column(DateTime)
    UpdatedDate = Column(DateTime)
    CreatedById = Column(Integer)


class Developer(Base):
    __tablename__ = "Developer"
    DeveloperId = Column(Integer(),
          primary_key=True,
          autoincrement=True,
    )
    DeveloperName = Column(String)
    DeveloperEmail = Column(String)
    DeveloperPhone = Column(BigInteger)
    DeveloperAddress = Column(String)
    DeveloperCity = Column(String)
    DeveloperState = Column(String)
    DeveloperPostalCode = Column(String)
    IsActive = Column(Boolean)
    CreatedDate = Column(DateTime)
    UpdatedDate = Column(DateTime)
    CreatedById = Column(Integer)


class InfraUnit(Base):
    __tablename__ = "infraunit"
    InfraUnitId = Column(Integer(),
                         primary_key=True,
                         autoincrement=True,
                         )
    # InfraId = Column(Integer)
    InfraId = Column(Integer, ForeignKey("infra.InfraId"), nullable=True)
    infra = relationship("Infra")
    UnitNumber = Column(String)
    FloorNumber = Column(Integer)
    UnitSize = Column(Float)
    AvailabilityStatus = Column(String)
    Direction = Column(String)
    UnitType = Column(String)
    View = Column(String)
    PurchaseReason = Column(String)
    CreatedDate = Column(DateTime)
    UpdateDate = Column(DateTime)
    CreatedById = Column(Integer)
    InfraType = Column(String)
    Active = Column(Boolean)


class Targets(Base):
    __tablename__ = 'targets'
    TargetId = Column(Integer(),
               primary_key = True,
               autoincrement=True,
    )
    TargetType = Column(String)
    TargetDescription = Column(String)
    TargetStartDate = Column(DateTime)
    TargetEndDate = Column(DateTime)
    TargetValue = Column(String)
    EvaluationCycle = Column(String)
    EvaluationDate = Column(DateTime)
    Is_Active = Column(Boolean)
    CreatedDate = Column(DateTime)
    UpdatedDate = Column(DateTime)
    CreatedById = Column(Integer)


class UserTargetAllotment(Base):
    __tablename__ = 'UserTargetAllotment'
    AllotmentId = Column(Integer(),
               primary_key = True,
               autoincrement=True,
    )
    AllotedToUserId = Column(Integer)
    TargetId = Column(Integer)
    AllottedValue = Column(Float)
    AchievedValue = Column(Float)
    AllotmentStatus = Column(String)
    AllotmentDate = Column(DateTime)
    CompletionDate = Column(DateTime)
    Remarks = Column(String)
    CreatedDate = Column(DateTime)
    UpdatedDate = Column(DateTime)


class  Contact(Base):
    __tablename__ = "contact"
    ContactId = Column(Integer(),
        primary_key=True,
        autoincrement=True,
    )
    ContactFName = Column(String)
    ContactLName = Column(String)
    ContactEmail = Column(String, nullable=True)
    ContactNo = Column(BigInteger)
    ContactCity = Column(String)
    ContactState = Column(String)
    ContactAddress = Column(String)
    ContactPostalCode = Column(String)
    ContactType = Column(String)
    AccountId = Column(Integer)
    BrokerLicence = Column(String)
    CommisionRate = Column(Float)
    YearsExperience = Column(Integer)
    Specialization = Column(String)
    ContactCountryCode = Column(String)
    CreatedDate = Column(DateTime)
    UpdatedDate = Column(DateTime)
    CreatedById = Column(Integer)
    Instagram = Column(String)
    Facebook = Column(String)
    Twitter = Column(String)



class Account(Base):
    __tablename__ = 'Account'
    AccountId = Column(Integer(),
                primary_key=True,
                autoincrement=True,
    )
    AccountName = Column(String)
    Industry = Column(String)
    Website = Column(String)
    Phone = Column(String)
    Address = Column(Text)
    AccountOwnerId = Column(Integer)
    CreatedDate = Column(DateTime)
    UpdatedDate = Column(DateTime)
    CreatedById = Column(Integer)


class Visit(Base):
    __tablename__ = 'Visit'
    VisitId = Column(Integer(),
              primary_key = True,
              autoincrement = True,
    )
    # ContactId = Column(Integer, ForeignKey("contact.ContactId"))
    # contact = relationship("Contact", foreign_keys=[ContactId])
    # BrokerId = Column(Integer)
    # BrokerId = Column(Integer, ForeignKey("contact.ContactId"), nullable=True)
    # broker = relationship("Contact", foreign_keys=[BrokerId])
    # LeadId = Column(Integer, ForeignKey("lead.LeadId"),nullable=True)
    # lead = relationship("Lead")
    InfraId = Column(Integer, ForeignKey("infra.InfraId"), nullable=True)
    infra = relationship("Infra")
    SiteId = Column(Integer, ForeignKey("site.SiteId"),nullable=True)
    site = relationship("Site")
    # InfraUnitId = Column(Integer, ForeignKey( "infraunit.InfraUnitId"))
    # infraunit = relationship("InfraUnit")
    # VisitType = Column(String)
    # PropertyType = Column(String)
    # Bedrooms = Column(Integer)
    # SizeSqFt = Column(Float)
    # ViewType = Column(String)
    # FloorPreference = Column(Integer)
    # BuyingIntent = Column(Integer)
    VisitDate = Column(DateTime)
    VisitStatus = Column(String)
    SalesPersonId = Column(Integer)
    Purpose = Column(String)
    # Notes = Column(Text)
    # VisitorFeedback = Column(Text)
    # FollowUpDate = Column(DateTime)
    # FollowUpStatus = Column(String)
    CreatedDate = Column(DateTime)
    UpdatedDate = Column(DateTime)
    VisitOutlook = Column(String)
    CreatedById = Column(Integer, ForeignKey("users.id"))
    created_by = relationship("Users")
    IsDeleted = Column(Integer, default=0)



class Lead(Base):
    __tablename__ = "lead"
    LeadId = Column(Integer(),
        primary_key=True,
        autoincrement=True,
    )
    LeadName = Column(String)
    ContactId = Column(Integer, ForeignKey("contact.ContactId"),nullable=True)
    contacts = relationship("Contact", foreign_keys=[ContactId])
    SiteId = Column(Integer, ForeignKey("site.SiteId"),nullable=True)
    site = relationship("Site")
    InfraId = Column(Integer)
    InfraUnitId = Column(Integer)
    ProspectTypeId =Column(Integer, ForeignKey("prospecttype.ProspectTypeId"),nullable=True)
    prospecttypes = relationship("ProspectType")
    CreatedById = Column (Integer, ForeignKey("users.id"))
    created_by = relationship("Users")
    CreatedDate = Column(DateTime)
    LeadClosedDate = Column(DateTime)
    UpdatedDate = Column(DateTime)
    QuotedAmount = Column(Double)
    RequestedAmount = Column(Double)
    ClosedAmount = Column(Double)
    LeadStatus = Column(String)
    BrokerId = Column(Integer, ForeignKey("contact.ContactId"),nullable=True)
    broker = relationship("Contact", foreign_keys=[BrokerId])
    LeadType = Column(String)
    LeadSource = Column(String)
    SuggestedUnitId = Column(Integer, ForeignKey("infraunit.InfraUnitId"), nullable=True)
    suggestedunit = relationship('InfraUnit')
    Bedrooms = Column(String)
    SizeSqFt = Column(Float)
    ViewType = Column(String)
    FloorPreference = Column(Integer)
    BuyingIntent = Column(Integer)
    LeadPriority = Column(Integer)
    LeadNotes = Column(Text)
    Direction = Column(String)
    Locality = Column(String)
    LostReasons = Column(String)
    # Lead Intelligence & Scoring Columns
    HealthScore = Column(Integer)
    VelocityScore = Column(Integer)
    AIPriority = Column(Integer)
    ConversionProbability = Column(DECIMAL(5,2))
    ChurnRisk = Column(String)
    FollowUpStatus = Column(String)
    OverdueDays = Column(Integer)
    RecommendationJson = Column(Text)
    ScoresLastUpdated = Column(DateTime)
    IsDeleted = Column(Integer, default=0)


class LeadVelocitySnapshots(Base):
    __tablename__ = 'lead_velocity_snapshots'
    SnapshotId = Column(Integer(),
                primary_key=True,
                autoincrement=True,
    )
    LeadId = Column(Integer, ForeignKey("lead.LeadId"), nullable=False)
    lead = relationship("Lead")
    SnapshotDate = Column(DateTime, nullable=False)
    HealthScore = Column(Integer, nullable=False)
    FollowUpCount = Column(Integer)
    InteractionCount = Column(Integer)
    ResponseRate = Column(DECIMAL(5,2))
    BuyingIntent = Column(Integer)
    DaysSinceCreated = Column(Integer)
    StageProgression = Column(Integer)


class FollowUps(Base):
    __tablename__ = 'FollowUps'
    FollowUpsId = Column(Integer(),
                primary_key=True,
                autoincrement=True,
    )
    # LeadId = Column(Integer)
    LeadId = Column(Integer, ForeignKey("lead.LeadId"))
    lead = relationship("Lead")
    # VisitId = Column(Integer)
    VisitId = Column(Integer, ForeignKey("Visit.VisitId"))
    visit = relationship("Visit")
    UserId = Column(Integer, ForeignKey("users.id"))
    user = relationship("Users")
    FollowUpType = Column(String)
    Status = Column(String)
    Notes = Column(Text)
    FollowUpDate = Column(DateTime)
    NextFollowUpDate = Column(DateTime)
    CreatedDate = Column(DateTime)
    UpdatedDate = Column(DateTime)
    CreatedById = Column(Integer)


class LeaveApplication(Base):
    __tablename__ = 'LeaveApplication'
    LeaveApplicationId = Column(Integer(),
                primary_key=True,
                autoincrement=True,
    )
    EmployeeId = Column(Integer, ForeignKey("users.id"), nullable=False)
    employeeid = relationship("Users")
    LeaveType = Column(String)
    StartDate = Column(DateTime)
    EndDate = Column(DateTime)
    Status = Column(String)
    BackupEmployeeId = Column(Integer, nullable=True)
    AutoReassign = Column(Boolean, nullable=True)
    Notes = Column(Text, nullable=True)
    CreatedDate = Column(DateTime)
    UpdatedDate = Column(DateTime)
    CreatedById = Column(Integer)


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer(),
        primary_key=True,
        autoincrement=True,
    )

    FirstName = Column(String)
    LastName = Column(String)
    Email = Column(String)
    username = Column(String)
    hashedpassword = Column(String)
    is_active = Column(Boolean,default=True)
    role = Column(String)
    ManagerId  = Column (Integer)
    ContactNo = Column (BigInteger)
    CreatedDate = Column(DateTime)
    UpdatedDate = Column(DateTime)
    CreatedBy = Column(Integer)



class Todos(Base):
    __tablename__ = "todos"
    TodosId = Column(Integer(),
        primary_key=True,
        autoincrement=True,
    )
    Title = Column(String)
    Description = Column(String)
    Priority = Column(Integer)
    Complete = Column(Boolean)
    UserId = Column(Integer,ForeignKey("users.id"), nullable=False)


class ActionItem(Base):
    __tablename__ = 'ActionItem'
    ActionItemId = Column(Integer(),
                   primary_key= True,
                   autoincrement=True,
    )

    lead = relationship("Lead")
    AllotedToUserId = Column(Integer, ForeignKey("users.id"))
    alloted_to_user_id = relationship("Users", foreign_keys=[AllotedToUserId])
    AllotedByUserId = Column(Integer, ForeignKey("users.id"))
    alloted_by_user_id = relationship("Users", foreign_keys=[AllotedByUserId])
    CreatedDate = Column(DateTime)
    UpdateDate = Column(DateTime)
    ProposedEndDate = Column(DateTime)
    ActualEndDate = Column(DateTime)
    Description = Column(String)
    Status = Column(String)
    ActionItemName = Column(String)
    LeadId = Column(Integer, ForeignKey("lead.LeadId"))
    VisitId = Column(Integer, ForeignKey("Visit.VisitId"))
    visit = relationship("Visit")
    FollowUpsId = Column(Integer, ForeignKey("FollowUps.FollowUpsId"))
    followup = relationship("FollowUps")


class ProspectType(Base):
    __tablename__ = 'prospecttype'
    ProspectTypeId = Column(Integer(),
        primary_key=True,
        autoincrement=True,
    )
    ProspectTypeName = Column (String)


class LeadHistory(Base):
    __tablename__ = "leadhistory"
    LeadHistoryId = Column(Integer(),
        primary_key=True,
        autoincrement=True,
    )
    LeadId = Column(Integer)
    UpdateName = Column(String)
    UpdateDetails = Column(String)


class AmenitySite(Base):
    __tablename__ = "AmenitySite"
    AmenitySiteId = Column(Integer(),
           primary_key=True,
           autoincrement=True,
    )
    AmenityId = Column(Integer)
    SiteId = Column(Integer)
    AllotmentDate = Column(DateTime)
    IsActive = Column(Boolean)


class SiteType(Base):
    __tablename__ = "sitetype"
    SiteTypeId = Column(Integer(),
         primary_key=True,
         autoincrement=True,
    )
    SiteType = Column(String)


class  Amenity(Base):
    __tablename__ = "amenity"
    AmenityId = Column(Integer(),
        primary_key=True,
        autoincrement=True,
    )
    AmenityName = Column(String)





class InfraType(Base):
    __tablename__ = "infratype"
    InfraTypeid = Column(Integer(),
        primary_key=True,
        autoincrement=True,
    )
    InfraTypeName = Column(String)




class Reports(Base):
    __tablename__ = "reports"
    ReportId = Column(Integer(),
       primary_key=True,
       autoincrement=True,
        )

    ReportName = Column(String)
    ReportFrequency = Column(String)
    DeliveryMethods = Column(String)
    CreatedDate = Column(DateTime)
    UpdatedDate = Column(DateTime)
    CreatedById = Column(Integer, ForeignKey("users.id"))
    created_by = relationship("Users")
    RecipientUserId = Column(Integer)
    PublishingDateTime = Column(DateTime)
    IsActive = Column(Boolean, default=True)





class Broker(Base):
    __tablename__ = "broker"
    Brokerid = Column(Integer(),
        primary_key=True,
        autoincrement=True,
    )

    BrokerFirstName = Column(String)
    BrokerLastName = Column(String)
    BrokerEmail = Column(String)
    BrokerCity = Column(String)
    BrokerAddress = Column(String)
    BrokerType = Column(String)
    is_active = Column(Boolean,default=True)



class Employees(Base):
    __tablename__ = "Employees"
    EmployeeID = Column(Integer(),
        primary_key=True,
        autoincrement=True,
    )

    EmployeeName = Column(String, nullable=True)
    Email = Column(String, nullable=True)
    PhoneNumber = Column(String, nullable=True)
    




class Visitors(Base):
    __tablename__ = "visitors"
    VisitorsId = Column(Integer(),
        primary_key=True,
        autoincrement=True,
    )
    VisitId = Column(Integer, ForeignKey("Visit.VisitId"))
    visit = relationship("Visit")
    ContactId = Column(Integer, ForeignKey("contact.ContactId"), nullable=True)
    contacts = relationship("Contact", foreign_keys=[ContactId])
    LeadId = Column(Integer, ForeignKey("lead.LeadId"), nullable=True)
    lead = relationship("Lead")
    InfraUnitId = Column(Integer, ForeignKey("infraunit.InfraUnitId"), nullable=True)
    infraunit = relationship("InfraUnit")
    VisitType = Column(String)
    PropertyType = Column(String)
    Bedrooms = Column(String)
    SizeSqFt = Column(Float)
    ViewType = Column(String)
    FloorPreference = Column(Integer)
    BuyingIntent = Column(Integer)
    # VisitStatus = Column(String)
    Notes = Column(Text)
    VisitorFeedback = Column(Text)
    FollowUpDate = Column(DateTime)
    FollowUpStatus = Column(String)
    # VisitOutlook = Column(String)
    CreatedDate = Column(DateTime)
    UpdatedDate = Column(DateTime)
    CreatedById = Column(Integer, ForeignKey("users.id"))
    created_by = relationship("Users")
    Direction = Column(String)
    IsDeleted = Column(String)



class APIConfiguration(Base):
    __tablename__ = "APIConfiguration"
    ConfigId = Column(Integer(),
        primary_key=True,
        autoincrement=True
    )
    ConfigKey = Column(String(100), nullable=True)
    ConfigValue = Column(String(500), nullable=True)
    ConfigProvider = Column(String(50), nullable=True)
    ConfigType = Column(String(50), nullable=True)
    WhatsAppFrom = Column(String(50), nullable=True)
    IsActive = Column(Boolean, nullable=True)
    IsEncrypted = Column(Boolean, nullable=True)
    CreatedAt = Column(DateTime, nullable=True)
    UpdatedAt = Column(DateTime, nullable=True)
    CreatedBy = Column(String(100), nullable=True)
    ContentTemplateSID = Column(String(100), nullable=True)


class NotificationConfiguration(Base):
    __tablename__ = "NotificationConfiguration"
    NotificationId = Column(Integer(),
        primary_key=True,
        autoincrement=True)

    SenderEmail = Column(String(100), nullable=False)
    SenderPassword = Column(String, nullable=False)
    RecipientEmail = Column(String(100), nullable=True)
    RecipientName = Column(String(100), nullable=True)
    SMTPServer = Column(String(100), nullable=True, default='smtp.gmail.com')
    SMTPPort = Column(Integer, nullable=True, default=587)
    IsActive = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime)
    UpdatedAt = Column(DateTime)
    CreatedById = Column(Integer, nullable=True)
    ToNumber = Column(String(50), nullable=True)
    SMSFrom = Column(String(50), nullable=True)


# -------------------------------------------------------------------------------------------

class Role(Base):
    __tablename__ = "Roles"
    RoleId = Column(Integer(),
        primary_key=True,
        autoincrement=True)
    Name = Column(String(100),  nullable=False)
    Description = Column(Text, nullable=True)
    IsSystemRole = Column(Boolean, nullable=False, default=False)
    Active = Column(Boolean, nullable=False, default=True)
    CreatedDate = Column(DateTime, nullable=False)
    UpdatedDate = Column(DateTime, nullable=False)
    CreatedBy = Column(Integer, ForeignKey("users.id"), nullable=False)
    HierarchyLevel = Column(Integer, nullable=False, default=1)


class UserRole(Base):
    __tablename__ = "UserRoles"
    UserRoleId = Column(Integer(),
        primary_key=True,
        autoincrement=True)
    UserId = Column(Integer, ForeignKey("users.id"), nullable=False)
    RoleId = Column(Integer, ForeignKey("Roles.RoleId"), nullable=False)
    IsActive = Column(Boolean, nullable=False, default=True)
    ExpiryDate = Column(DateTime, nullable=True)
    AssignedBy = Column(Integer, ForeignKey("users.id"), nullable=False)
    Notes = Column(Text, nullable=True)
    CreatedDate = Column(DateTime, nullable=False)
    UpdatedDate = Column(DateTime, nullable=False)



class PermissionAssignment(Base):
    __tablename__ = "PermissionAssignments"
    AssignmentId = Column(Integer(),
        primary_key=True,
        autoincrement=True)
    PermissionId = Column(Integer, ForeignKey("Permissions.PermissionId"), nullable=False)
    UserId = Column(Integer, ForeignKey("users.id"), nullable=True)
    RoleId = Column(Integer, ForeignKey("Roles.RoleId"), nullable=True)
    AssignmentType = Column(String(10), nullable=False)
    IsGranted = Column(Boolean, nullable=False, default=True)
    ExpiresAt = Column(DateTime, nullable=True)
    Reason = Column(Text, nullable=True)
    GrantedAt = Column(DateTime, nullable=False)
    GrantedBy = Column(Integer, ForeignKey("users.id"), nullable=False)
    UpdatedAt = Column(DateTime, nullable=False)


class Permission(Base):
    __tablename__ = "Permissions"
    PermissionId = Column(Integer(),
        primary_key=True,
        autoincrement=True)
    Name = Column(String(100), nullable=False)
    Code = Column(String(100),  nullable=False)
    Description = Column(Text, nullable=True)
    PermissionType = Column(String(10), nullable=False, default="DATA")
    ResourceType = Column(String(50), nullable=True)
    OperationType = Column(String(50), nullable=True)
    UIComponent = Column(String(100), nullable=True)
    UIAction = Column(String(50), nullable=True)
    FilterLogic = Column(String(500), nullable=True)
    RiskLevel = Column(String(10), nullable=False, default="LOW")
    Category = Column(String(50), nullable=True)
    Active = Column(Boolean, nullable=False, default=True)
    CreatedAt = Column(DateTime, nullable=False)
    UpdatedAt = Column(DateTime, nullable=False)



class PermissionFilter(Base):
    __tablename__ = "PermissionFilters"
    FilterId = Column(Integer(),
        primary_key=True,
        autoincrement=True)
    PermissionId = Column(Integer, ForeignKey("Permissions.PermissionId"), nullable=False)
    FilterGroupId = Column(String(10), nullable=True)
    MasterAttribute = Column(String(100), nullable=False)
    Operator = Column(String(20), nullable=False)
    DataHierarchy = Column(String(20), nullable=False, default="ALL")
    IsDynamic = Column(Boolean, nullable=False, default=False)
    CreatedAt = Column(DateTime, nullable=False,)


class PermissionFilterValue(Base):
    __tablename__ = "PermissionFilterValues"
    ValueId = Column(Integer, primary_key=True,  autoincrement=True)
    FilterId = Column(Integer, ForeignKey("PermissionFilters.FilterId"), nullable=False)
    Value = Column(String(500), nullable=False)
    ValueType = Column(String(10), nullable=False, default="STRING")
    Sequence = Column(Integer, nullable=False, default=1)




class ColumnMapping(Base):
    __tablename__ = "ColumnMapping"
    ColumnMappingId = Column(Integer, primary_key=True, index=True)
    ModelName = Column(String, nullable=True)
    ExcelColumn = Column(String, nullable=True)
    DbColumn = Column(String, nullable=True)
    CreatedAt = Column(DateTime)  # store UTC


class TempUpload(Base):
    __tablename__ = "TempUpload"

    TempUploadId = Column(Integer, primary_key=True, index=True)
    ModelName = Column(String, nullable=False)

    # Contact
    ContactFName = Column(String, nullable=True)
    ContactLName = Column(String, nullable=True)
    ContactNo = Column(String, nullable=True)
    ContactType = Column(String, nullable=True)

    # Site
    SiteName = Column(String, nullable=True)
    SiteCity = Column(String, nullable=True)
    SiteAddress = Column(String, nullable=True)
    SiteStatus = Column(String, nullable=True)
    SiteDescription = Column(String, nullable=True)
    IsOperational = Column(Boolean, nullable=True)

    # Lead
    LeadName = Column(String, nullable=True)
    ContactId = Column(Integer, nullable=True)
    SiteId = Column(Integer, nullable=True)
    CreatedDate = Column(DateTime, nullable=True)
    LeadClosedDate = Column(DateTime, nullable=True)
    LeadStatus = Column(String, nullable=True)
    LeadSource = Column(String, nullable=True)
    LeadNotes = Column(String, nullable=True)
    uploaded_at = Column(DateTime)  # store UTC

    BrokerFName = Column(String(100), nullable=True)
    BrokerLName = Column(String(100), nullable=True)
    BrokerNo = Column(String(20), nullable=True)
    SiteType = Column(String(50), nullable=True)
    Bedrooms = Column(String(10), nullable=True)
    SizeSqFt = Column(Float, nullable=True)
    ViewType = Column(String(50), nullable=True)
    FloorPreference = Column(Integer, nullable=True)
    BuyingIntent = Column(Integer, nullable=True)
    Direction = Column(String(50), nullable=True)
    Locality = Column(String(100), nullable=True)
    LostReasons = Column(String(255), nullable=True)
    UploadFileId = Column(BigInteger, ForeignKey('FileTracker.FileId', ondelete='CASCADE'), nullable=True)

# ------------------------------------------------------------------------------------------------------------


class FileTracker(Base):
    __tablename__ = "FileTracker"

    FileId = Column(Integer, primary_key=True, autoincrement=True)
    FileName = Column(String(500))
    FileExtension = Column(String(500), Computed("..."))
    FileSize = Column(BigInteger)
    Status = Column(String)
    IsLoaded = Column(Integer, Computed("..."))
    Priority = Column(Integer)
    SourceTableName = Column(String(255))
    DestinationTableName = Column(String(255))
    SourceSchema = Column(String(255))
    DestinationSchema = Column(String(255))
    RecordsExpected = Column(Integer)
    RecordsProcessed = Column(Integer)
    RecordsFailed = Column(Integer)
    CreatedDate = Column(DateTime)
    ModifiedDate = Column(DateTime)
    ProcessStartTime = Column(DateTime)
    ProcessEndTime = Column(DateTime)
    ProcessingDuration = Column(Integer, Computed("..."))  # in seconds
    UploadedBy = Column(String)


class ContactTemp(Base):
    __tablename__ = "ContactTemp"
    ContactTempId = Column(Integer, primary_key=True, autoincrement=True)
    UploadFileId = Column(BigInteger, ForeignKey('FileTracker.FileId', ondelete='CASCADE'), nullable=True)
    uploadfiles = relationship("FileTracker", foreign_keys=[UploadFileId])
    ContactFName = Column(String(255), nullable=True)
    ContactLName = Column(String(255), nullable=True)
    ContactNo = Column(String(50), nullable=True)
    ContactType = Column(String(100), nullable=True)
    uploaded_at = Column(DateTime)


class SiteTemp(Base):
    __tablename__ = "SiteTemp"
    SiteTempId = Column(Integer, primary_key=True, autoincrement=True)
    UploadFileId = Column(BigInteger, ForeignKey('FileTracker.FileId', ondelete='CASCADE'), nullable=True)
    uploadfiles = relationship("FileTracker", foreign_keys=[UploadFileId])
    SiteName = Column(String(255), nullable=True)
    SiteCity = Column(String(255), nullable=True)
    SiteAddress = Column(String(500), nullable=True)
    SiteStatus = Column(String(100), nullable=True)
    SiteDescription = Column(String(1000), nullable=True)
    IsOperational = Column(Boolean, nullable=True)
    SiteType = Column(String(50), nullable=True)
    uploaded_at = Column(DateTime)


class LeadTemp(Base):
    __tablename__ = "LeadTemp"

    LeadTempId = Column(Integer, primary_key=True, autoincrement=True)
    UploadFileId = Column(BigInteger, ForeignKey('FileTracker.FileId', ondelete='CASCADE'), nullable=True)
    uploadfiles = relationship("FileTracker", foreign_keys=[UploadFileId])
    LeadName = Column(String(255), nullable=True)
    ContactId = Column(Integer, nullable=True)
    SiteId = Column(Integer, nullable=True)
    CreatedDate = Column(DateTime, nullable=True)
    LeadClosedDate = Column(DateTime, nullable=True)
    LeadStatus = Column(String(100), nullable=True)
    LeadSource = Column(String(100), nullable=True)
    LeadNotes = Column(String(1000), nullable=True)
    Bedrooms = Column(String(10), nullable=True)
    SizeSqFt = Column(Float, nullable=True)
    ViewType = Column(String(50), nullable=True)
    FloorPreference = Column(Integer, nullable=True)
    BuyingIntent = Column(Integer, nullable=True)
    Direction = Column(String(50), nullable=True)
    Locality = Column(String(100), nullable=True)
    LostReasons = Column(String(255), nullable=True)
    uploaded_at = Column(DateTime)


class BrokerTemp(Base):
    __tablename__ = "BrokerTemp"

    BrokerTempId = Column(Integer, primary_key=True, autoincrement=True)
    UploadFileId = Column(BigInteger, ForeignKey('FileTracker.FileId', ondelete='CASCADE'), nullable=True)
    uploadfiles = relationship("FileTracker", foreign_keys=[UploadFileId])
    BrokerFName = Column(String(100), nullable=True)
    BrokerLName = Column(String(100), nullable=True)
    BrokerNo = Column(String(20), nullable=True)
    uploaded_at = Column(DateTime)


class WhatsAppConversation(Base):
    """
    Stores WhatsApp conversation history for context management.
    Replaces Redis for conversation memory.
    """
    __tablename__ = "WhatsAppConversations"

    Id = Column(Integer(), primary_key=True, autoincrement=True)
    PhoneNumber = Column(String(50), nullable=False, index=True)
    UserMessage = Column(Text)
    BotResponse = Column(Text)
    Intent = Column(String(100))
    Entities = Column(Text)  # JSON string of extracted entities
    Timestamp = Column(DateTime, nullable=False)
    SessionId = Column(String(100), nullable=False, index=True)
    LeadId = Column(Integer, ForeignKey("lead.LeadId"), nullable=True)
    lead = relationship("Lead", foreign_keys=[LeadId])
    ContactId = Column(Integer, ForeignKey("contact.ContactId"), nullable=True)
    contact = relationship("Contact", foreign_keys=[ContactId])
    VisitId = Column(Integer, ForeignKey("Visit.VisitId"), nullable=True)
    visit = relationship("Visit", foreign_keys=[VisitId])
    CreatedDate = Column(DateTime)
    UpdatedDate = Column(DateTime)


class Brochure(Base):
    """
    Stores brochure data extracted from files.
    Allows dynamic updates to property information for WhatsApp bot responses.
    """
    __tablename__ = "Brochure"

    BrochureId = Column(Integer(), primary_key=True, autoincrement=True)
    ProjectName = Column(String(200), nullable=False, index=True)
    SiteId = Column(Integer, ForeignKey("site.SiteId"), nullable=True)
    site = relationship("Site", foreign_keys=[SiteId])
    FileName = Column(String(500))
    FilePath = Column(String(1000))
    FileSize = Column(BigInteger)  # Size in bytes
    RawText = Column(Text)  # Full extracted text from file
    StructuredData = Column(JSON)  # JSON structured data
    IsActive = Column(Boolean, default=True)  # Support multiple versions
    IsDeleted = Column(Boolean, default=False)
    CreatedDate = Column(DateTime, nullable=False)
    UpdatedDate = Column(DateTime)
    CreatedById = Column(Integer, ForeignKey("users.id"))
    UpdatedById = Column(Integer, ForeignKey("users.id"))
    created_by = relationship("Users", foreign_keys=[CreatedById])
    updated_by = relationship("Users", foreign_keys=[UpdatedById])