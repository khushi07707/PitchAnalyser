using System;

namespace AIAugmentedPitchAnalyzer.Application.DTOs.User
{
    public class UserDto
    {
        public Guid Id { get; set; }
        public string FirstName { get; set; } = null!;
        public string? LastName { get; set; }
        public string Email { get; set; } = null!;
        public Guid RoleId { get; set; }
    }
}
