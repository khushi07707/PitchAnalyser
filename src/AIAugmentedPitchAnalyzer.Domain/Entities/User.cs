using System;
using System.Collections.Generic;

namespace AIAugmentedPitchAnalyzer.Domain.Entities
{
    /// <summary>
    /// Application user (founder / admin / reviewer) entity.
    /// </summary>
    public class User : BaseEntity
    {
        public string FirstName { get; set; } = null!;
        public string? LastName { get; set; }
        public string Email { get; set; } = null!;
        public string PasswordHash { get; set; } = null!;
        public Guid RoleId { get; set; }
        public Role? Role { get; set; }

        public ICollection<Startup>? Startups { get; set; }
        public ICollection<FileRecord>? UploadedFiles { get; set; }
    }
}
