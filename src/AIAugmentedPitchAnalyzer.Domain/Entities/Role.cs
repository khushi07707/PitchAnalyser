using System.Collections.Generic;

namespace AIAugmentedPitchAnalyzer.Domain.Entities
{
    /// <summary>
    /// Role entity for RBAC.
    /// </summary>
    public class Role : BaseEntity
    {
        public string Name { get; set; } = null!;
        public string? Description { get; set; }

        public ICollection<User>? Users { get; set; }
    }
}
