using System;

namespace AIAugmentedPitchAnalyzer.Domain.Entities
{
    /// <summary>
    /// Base entity with common audit fields.
    /// </summary>
    public abstract class BaseEntity
    {
        /// <summary>
        /// Primary key of the entity.
        /// </summary>
        public Guid Id { get; set; } = Guid.NewGuid();

        /// <summary>
        /// Creation timestamp in UTC.
        /// </summary>
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

        /// <summary>
        /// Last update timestamp in UTC.
        /// </summary>
        public DateTime? UpdatedAt { get; set; }

        /// <summary>
        /// Soft-delete flag.
        /// </summary>
        public bool IsDeleted { get; set; } = false;
    }
}
