from enum import Enum

class Role(Enum):
    STAFF = "staff"
    ATTENDEE = "attendee"

    def is_authorized(self, min_role: "Role"):
        """
        Check if the role is authorized following the hirearchy and giving
        a minimum role for the specific task
        """
        roles_hierarchy = {
            Role.STAFF: 2,
            Role.ATTENDEE: 1
        }
        return roles_hierarchy[self] >= roles_hierarchy[min_role]
