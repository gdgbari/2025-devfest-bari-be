import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    STAFF = "staff"
    SPEAKER = "speaker"
    ATTENDEE = "attendee"
    TEST = "test"
    
    def is_authorized(self, min_role: "UserRole"):
        roles_hierarchy = {
            UserRole.ADMIN: 4,
            UserRole.STAFF: 3,
            UserRole.SPEAKER: 2,
            UserRole.ATTENDEE: 1,
            UserRole.TEST: 1,
        }
        return roles_hierarchy[self] >= roles_hierarchy[min_role]