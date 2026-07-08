using System;

namespace AIAugmentedPitchAnalyzer.Application.DTOs.File
{
    public class FileRecordDto
    {
        public Guid Id { get; set; }
        public string FileName { get; set; } = null!;
        public string FilePath { get; set; } = null!;
        public string ContentType { get; set; } = null!;
        public long Size { get; set; }
        public DateTime UploadedAt { get; set; }
        public Guid? UploadedById { get; set; }
        public Guid? PitchId { get; set; }
    }
}
