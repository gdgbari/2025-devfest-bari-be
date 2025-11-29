from enum import Enum

class Role(Enum):
    ADMIN = "admin"
    STAFF = "staff"
    SPEAKER = "speaker"
    ATTENDEE = "attendee"

    def is_authorized(self, min_role: "Role"):
        """
        Check if the role is authorized following the hirearchy and giving
        a minimum role for the specific task
        """
        roles_hierarchy = {
            Role.ADMIN: 4,
            Role.STAFF: 3,
            Role.SPEAKER: 2,
            Role.ATTENDEE: 1
        }
        return roles_hierarchy[self] >= roles_hierarchy[min_role]
