from xmlrpc.client import DateTime

from pydantic import BaseModel, Field, EmailStr, conint, condecimal
from datetime import datetime, time

from decimal import Decimal
from typing import Optional, List



class LeadRequest (BaseModel):
    LeadName :  str = Field(min_length=3,max_length=100)
    ContactId: Optional[int] = None
    SiteId : Optional[int] = None
    InfraId : Optional[int] = None
    InfraUnitId :Optional[int] = None
    ProspectTypeId : Optional[int] = None
    # LeadClosedDate : Optional[datetime] = None
    QuotedAmount : Optional[Decimal] = None
    RequestedAmount : Optional[Decimal] = None
    ClosedAmount : Optional[Decimal] = None
    LeadStatus :  str= Field(default='New')
    BrokerId : Optional[int] = None
    SuggestedUnitId : Optional[int] = None
    Bedrooms : Optional[str] = None
    SizeSqFt : Optional[float] = None
    ViewType : Optional[str] = None
    FloorPreference : Optional[int] = None
    BuyingIntent : Optional[int] = None
    LeadPriority : Optional[int] = None
    LeadType : Optional[str] = None
    LeadSource : Optional[str] = None
    LeadNotes : Optional[str] = None
    Direction : Optional[str] = None
    Locality : Optional[str] = None
    LostReasons : Optional[str] = None




class SiteRequest (BaseModel):
    SiteName : str = Field(min_length=1, strip_whitespace=True, description="Site name cannot be empty")
    SiteTypeId : int
    SiteCity : str
    SiteStatus : str
    SiteAddress : Optional[str] = None
    SiteSizeSqFt : Optional[float] = None
    OperationalDate: Optional[datetime] = None
    IsOperational : Optional[bool] = None
    DeveloperId : Optional[int] = None
    SiteDescription : Optional[str] = None
    NearbyLandmarks : Optional[str] = None
    # CreatedDate : datetime
    # UpdateDate : datetime
    # CreatedById : int


class ContactRequest (BaseModel):
    ContactFName : str
    ContactLName : str
    ContactNo: conint(ge=1000000000, le=9999999999)  # Ensures 10-digit number
    ContactCountryCode : str
    ContactType : str

    ContactEmail : Optional[str] = None
    ContactCity : Optional[str] = None
    ContactState : Optional[str] = None
    ContactAddress : Optional[str] = None
    ContactPostalCode : Optional[str] = None
    AccountId : Optional[int] = None
    BrokerLicence : Optional[str] = None
    CommisionRate : Optional[float] = None
    YearsExperience : Optional[int] = None
    Specialization : Optional[str] = None
    Instagram : Optional[str] = None
    Facebook : Optional[str] = None
    Twitter : Optional[str] = None
    # CreatedDate : datetime
    # CreatedDate : datetime
    # UpdatedDate : datetime
    # CreatedById : int




class ProspectTypeRequest (BaseModel):
    ProspectTypeName: str = Field(min_length=1, strip_whitespace=True, description="Prospect type name cannot be empty")


class BrokerRequest (BaseModel):
    BrokerFirstName : str
    BrokerLastName : str
    BrokerEmail : EmailStr
    BrokerCity : str
    BrokerAddress : str
    BrokerType : str
    is_active : bool


class InfraTypeRequest (BaseModel):
    InfraTypeName : str



class SiteInfraRequest (BaseModel):
    # SiteId : int
    # InfraId : int
    # InfraUnitId : int
    InfraType : str
    Active : bool
    # CreatedDate : datetime
    # UpdatedDate : datetime
    # CreatedById : int

BigInt = conint(ge=1000000000, le=9999999999)

class DeveloperRequest (BaseModel):
    DeveloperName : str
    DeveloperEmail : EmailStr
    DeveloperPhone : BigInt
    DeveloperAddress : str
    DeveloperCity : str
    DeveloperState : str
    DeveloperPostalCode : str
    IsActive : bool
    CreatedDate : datetime
    UpdatedDate : datetime
    CreatedById : int


class InfraRequest (BaseModel):
    InfraName : str
    InfraCategory : str
    TotalUnits : str
    AvailableUnits : int
    SoldUnits : int
    BookedUnits : int
    InfraFloorCount : int
    SiteId : int
    # CreatedDate : datetime
    # UpdatedDate : datetime
    # CreatedById : int
    


class InfraUnitRequest (BaseModel):
    InfraId : int
    UnitNumber : str
    FloorNumber : int
    UnitSize : float
    AvailabilityStatus : str
    Direction : str
    UnitType : str
    View : str
    PurchaseReason : str
    # CreatedDate : datetime
    # UpdateDate : datetime
    # CreatedById : int
    # siteinfra: Optional[SiteInfraRequest] = None
    InfraType : str
    Active : bool= Field(default='True')


class AmenityRequest (BaseModel):
    AmenityName: str = Field(min_length=1, strip_whitespace=True, description="Amenity name cannot be empty")


class LeadHistoryRequest (BaseModel):
    LeadId : int
    UpdateName : str
    UpdateDetails : str



class ActionItemRequest (BaseModel):
    LeadId: Optional[int] = None
    VisitId: Optional[int] = None
    AllotedToUserId : Optional[int] = None
    ProposedEndDate : Optional[datetime] = None
    Description : Optional[str] = None
    Status : str= Field(default='New')
    ActionItemName : str



class TargetsRequest (BaseModel):
    TargetType : str
    TargetDescription : str
    TargetStartDate  : datetime
    TargetEndDate : datetime
    TargetValue : str
    EvaluationCycle : str
    EvaluationDate : datetime
    Is_Active : bool
    CreatedDate : datetime
    UpdatedDate : datetime
    CreatedById : int


class UserTargetAllotmentRequest (BaseModel):
    AllotedToUserId : int
    TargetId : int
    AllottedValue : float
    AchievedValue : float
    AllotmentStatus : str
    AllotmentDate : datetime
    CompletionDate : datetime
    Remarks : str
    CreatedDate : datetime
    UpdatedDate : datetime


class AccountRequest (BaseModel):
    AccountName : str
    Industry : str
    Website : str
    Phone : BigInt
    Address : str
    AccountOwnerId : int
    CreatedDate : datetime
    UpdatedDate : datetime
    CreatedById : int


class FollowUpsRequest (BaseModel):
   LeadId : Optional[int] = None
   VisitId : Optional[int] = None
   UserId : int
   FollowUpType : str
   Status : str
   Notes : Optional[str] = None
   FollowUpDate : datetime
   NextFollowUpDate : datetime
   # CreatedDate : datetime
   # UpdatedDate : datetime
   # CreatedById : int


class LeavesRequest (BaseModel):
    EmployeeId : int
    LeaveType : str
    StartDate : datetime
    EndDate : datetime
    Status : str
    BackupEmployeeId : Optional[int] = None
    AutoReassign : Optional[bool] = None
    Notes : Optional[str] = None
    # CreatedDate : datetime
    # UpdatedDate : datetime
    # CreatedById : int



class AmenitySiteRequest (BaseModel):
    AmenityId : int
    SiteId : int
    AllotmentDate : datetime
    IsActive : bool


class SiteTypeRequest (BaseModel):
    SiteType: str = Field(min_length=1, strip_whitespace=True, description="Site type cannot be empty")


class VisitRequest (BaseModel):
    # ContactId : int
    # BrokerId : int
    # LeadId : Optional[int] = None
    InfraId : Optional[int] = None
    SiteId : int
    # InfraUnitId : Optional[int] = None
    # VisitType : Optional[str] = None
    # PropertyType : Optional[str] = None
    # Bedrooms : Optional[int] = None
    # SizeSqFt : Optional[float] = None
    # ViewType : Optional[str] = None
    # FloorPreference : Optional[int] = None
    # BuyingIntent : Optional[int] = None
    VisitDate :  datetime
    VisitStatus : Optional[str] = None
    SalesPersonId : int
    Purpose : Optional[str] = None
    # Notes : Optional[str] = None
    # VisitorFeedback : Optional[str] = None
    # FollowUpDate : Optional[datetime] = None
    # FollowUpStatus : Optional[str] = None
    # CreatedDate : datetime
    # UpdatedDate : datetime
    VisitOutlook : Optional[str] = None
    # CreatedById : int




class ReportsRequest (BaseModel):
    ReportName : str
    ReportFrequency : str
    DeliveryMethods : str
    RecipientUserId : int
    PublishingDateTime : datetime
    IsActive : bool
    # CreatedDate : datetime
    # UpdatedDate : datetime



class VisitorCreate (BaseModel):
    ContactId : int
    LeadId : Optional[int] = None
    InfraUnitId : Optional[int] = None
    VisitType : Optional[str] = None
    PropertyType : Optional[str] = None
    Bedrooms : Optional[str] = None
    SizeSqFt : Optional[float] = None
    ViewType : Optional[str] = None
    FloorPreference : Optional[int] = None
    BuyingIntent : Optional[int] = None
    # VisitStatus : Optional[str] = None
    Notes : Optional[str] = None
    VisitorFeedback : Optional[str] = None
    FollowUpDate : Optional[datetime] = None
    FollowUpStatus : Optional[str] = None
    Direction : Optional[str] = None
    IsDeleted :  Optional[str]= Field(default='No')

    # VisitOutlook : Optional[str] = None

class VisitorsRequest(BaseModel):
    VisitId: Optional[int] = None  # Optional if you're creating a new visit
    Visitors: List[VisitorCreate]





class ReportsRequest (BaseModel):
    ReportName : str
    ReportFrequency : str
    DeliveryMethods : str
    RecipientUserId : int
    PublishingDateTime : datetime
    IsActive : bool
    # CreatedDate : datetime
    # UpdatedDate : datetime


class APIConfigurationBase(BaseModel):
    ConfigKey: Optional[str]
    ConfigValue: Optional[str]
    ConfigProvider: Optional[str]
    ConfigType: Optional[str]
    WhatsAppFrom: Optional[str]
    IsActive: Optional[bool]
    IsEncrypted: Optional[bool] = None
    ContentTemplateSID: Optional[str]
    # CreatedAt: Optional[datetime]
    # UpdatedAt: Optional[datetime]
    # CreatedBy: Optional[str]


class NotificationConfigurationBase(BaseModel):
    SenderEmail: EmailStr
    SenderPassword: str
    RecipientEmail: Optional[EmailStr] = None
    RecipientName: Optional[str] = None
    SMTPServer: Optional[str] = "smtp.gmail.com"
    SMTPPort: Optional[int] = 587
    IsActive: bool = True
    # CreatedById: Optional[int] = None
    ToNumber: Optional[str] = None
    SMSFrom: Optional[str] = None




# ------------------------------------------------------------------------------------------

class RolesRequest(BaseModel):
    Name : Optional[str] = None
    Description : Optional[str] = None
    IsSystemRole : Optional[bool] = None
    Active : Optional[bool] = None
    # CreatedDate : Optional[datetime] = None
    # UpdatedDate : Optional[datetime] = None
    # CreatedBy : Optional[int] = None
    HierarchyLevel : Optional[int] = None
    site : List[int]



class UsersRolesRequest(BaseModel):
    UserId : Optional[int] = None
    RoleId : Optional[int] = None
    IsActive : Optional[bool] = None
    ExpiryDate : Optional[datetime] = None
    # AssignedBy : Optional[int] = None
    Notes : Optional[str] = None
    # CreatedDate : Optional[datetime] = None
    # UpdatedDate : Optional[datetime] = None


class PermissionAssignmentRequest(BaseModel):
    PermissionId : Optional[int] = None
    UserId : Optional[int] = None
    RoleId : Optional[int] = None
    AssignmentType : Optional[str] = None
    IsGranted : Optional[bool] = None
    ExpiresAt : Optional[datetime] = None
    Reason : Optional[str] = None
    # GrantedAt : Optional[datetime] = None
    # GrantedBy : Optional[int] = None
    # UpdatedAt : Optional[datetime] = None


class PermissionsRequest(BaseModel):
    Name : Optional[str] = None
    Code : Optional[str] = None
    Description : Optional[str] = None
    PermissionType : Optional[str] = None
    ResourceType : Optional[str] = None
    OperationType : Optional[str] = None
    UIComponent : Optional[str] = None
    UIAction : Optional[str] = None
    FilterLogic : Optional[str] = None
    RiskLevel : Optional[str] = None
    Category : Optional[str] = None
    Active : Optional[bool] = None
    # CreatedAt : Optional[datetime] = None
    # UpdatedAt : Optional[datetime] = None


class PermissionFiltersRequest(BaseModel):
    PermissionId : Optional[int] = None
    FilterGroupId : Optional[int] = None
    MasterAttribute : Optional[str] = None
    Operator : Optional[str] = None
    DataHierarchy : Optional[str] = None
    IsDynamic : Optional[bool] = None
    CreatedAt : Optional[datetime] = None


class PermissionFiltersValuesRequest(BaseModel):
    FilterId : Optional[int] = None
    Value : Optional[str ] = None
    ValueType : Optional[str] = None
    Sequence : Optional[int] = None



class ColumnMappingRequest(BaseModel):
    ModelName: Optional[str] = None
    ExcelColumn: Optional[str] = None
    DbColumn: Optional[str] = None


class TempUploadRequest(BaseModel):
    ModelName: str
    # Contact
    ContactFName: Optional[str] = None
    ContactLName: Optional[str] = None
    ContactNo: Optional[str] = None
    ContactType: Optional[str] = None

    # Site
    SiteName: Optional[str] = None
    SiteCity: Optional[str] = None
    SiteAddress: Optional[str] = None
    SiteStatus: Optional[str] = None
    SiteDescription: Optional[str] = None
    IsOperational: Optional[bool] = None

    # Lead
    LeadName: Optional[str] = None
    ContactId: Optional[int] = None
    SiteId: Optional[int] = None
    CreatedDate: Optional[datetime] = None
    LeadClosedDate: Optional[datetime] = None
    LeadStatus: Optional[str] = None
    LeadSource: Optional[str] = None
    LeadNotes: Optional[str] = None

    BrokerFName: Optional[str] = None
    BrokerLName: Optional[str] = None
    BrokerNo: Optional[str] = None
    SiteType: Optional[str] = None
    Bedrooms: Optional[str] = None
    SizeSqFt: Optional[float] = None
    ViewType: Optional[str] = None
    FloorPreference: Optional[int] = None
    BuyingIntent: Optional[int] = None
    Direction: Optional[str] = None
    Locality: Optional[str] = None
    LostReasons: Optional[str] = None



# ------------------------------------------------------------------------------------------------------------------

class FileTrackerBase(BaseModel):
    FileName: str
    FileSize: Optional[int]
    Status: Optional[str]
    Priority: Optional[int]
    SourceTableName: Optional[str]
    DestinationTableName: Optional[str]
    SourceSchema: Optional[str]
    DestinationSchema: Optional[str]
    RecordsExpected: Optional[int]
    RecordsProcessed: Optional[int]
    RecordsFailed: Optional[int]
    # CreatedDate: Optional[datetime]
    # ModifiedDate: Optional[datetime]
    # ProcessStartTime: Optional[datetime]
    # ProcessEndTime: Optional[datetime]
    UploadedBy: Optional[str]


class ContactTempBase(BaseModel):
    UploadFileId: Optional[int]
    ContactFName: Optional[str]
    ContactLName: Optional[str]
    ContactNo: Optional[str]
    ContactType: Optional[str]
    # uploaded_at: Optional[datetime]


class SiteTempBase(BaseModel):
    UploadFileId: Optional[int]
    SiteName: Optional[str]
    SiteCity: Optional[str]
    SiteAddress: Optional[str]
    SiteStatus: Optional[str]
    SiteDescription: Optional[str]
    IsOperational: Optional[bool]
    SiteType: Optional[str]
    # uploaded_at: Optional[datetime]


class LeadTempBase(BaseModel):
    UploadFileId: Optional[int]
    LeadName: Optional[str]
    ContactId: Optional[int]
    SiteId: Optional[int]
    CreatedDate: Optional[datetime]
    LeadClosedDate: Optional[datetime]
    LeadStatus: Optional[str]
    LeadSource: Optional[str]
    LeadNotes: Optional[str]
    Bedrooms: Optional[str]
    SizeSqFt: Optional[float]
    ViewType: Optional[str]
    FloorPreference: Optional[int]
    BuyingIntent: Optional[int]
    Direction: Optional[str]
    Locality: Optional[str]
    LostReasons: Optional[str]
    # uploaded_at: Optional[datetime]


class BrokerTempBase(BaseModel):
    UploadFileId: Optional[int]
    BrokerFName: Optional[str]
    BrokerLName: Optional[str]
    BrokerNo: Optional[str]
    # uploaded_at: Optional[datetime]


class WhatsAppConversationRequest(BaseModel):
    PhoneNumber: str = Field(min_length=10, max_length=50, description="Phone number in E.164 format or cleaned format")
    UserMessage: Optional[str] = None
    BotResponse: Optional[str] = None
    Intent: Optional[str] = None
    Entities: Optional[str] = None  # JSON string of extracted entities
    SessionId: str = Field(min_length=1, description="Unique session identifier")
    LeadId: Optional[int] = None
    ContactId: Optional[int] = None


class WhatsAppConversationResponse(BaseModel):
    Id: int
    PhoneNumber: str
    UserMessage: Optional[str]
    BotResponse: Optional[str]
    Intent: Optional[str]
    Entities: Optional[str]
    SessionId: str
    LeadId: Optional[int]
    ContactId: Optional[int]
    Timestamp: datetime
    CreatedDate: Optional[datetime]
    UpdatedDate: Optional[datetime]

    class Config:
        from_attributes = True  # Allows creation from ORM models


class WhatsAppConversationStats(BaseModel):
    """Schema for conversation statistics endpoint"""
    total_messages: int = Field(description="Total number of WhatsApp messages")
    unique_users: int = Field(description="Number of unique phone numbers")
    total_sessions: int = Field(description="Total number of conversation sessions")
    intents: dict = Field(description="Count of messages by intent type")