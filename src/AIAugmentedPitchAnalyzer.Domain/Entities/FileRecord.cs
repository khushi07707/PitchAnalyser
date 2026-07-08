using System;

namespace AIAugmentedPitchAnalyzer.Domain.Entities
{
    /// <summary>
    /// Metadata for uploaded files stored on disk.
    /// </summary>
    public class FileRecord : BaseEntity
    {
        public string FileName { get; set; } = null!;
        public string FilePath { get; set; } = null!;
        public string ContentType { get; set; } = null!;
        public long Size { get; set; }
        public DateTime UploadedAt { get; set; } = DateTime.UtcNow;

        public Guid UploadedById { get; set; }
        public User? UploadedBy { get; set; }

        public Guid? PitchId { get; set; }
        public Pitch? Pitch { get; set; }
    }
}
