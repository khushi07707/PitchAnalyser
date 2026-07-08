using System;

namespace AIAugmentedPitchAnalyzer.Application.DTOs.Pitch
{
    public class PitchDto
    {
        public Guid Id { get; set; }
        public string Title { get; set; } = null!;
        public DateTime UploadedAt { get; set; }
        public Guid? FileRecordId { get; set; }
        public string? ExtractedText { get; set; }
        public PitchAnalysisDto? Analysis { get; set; }
    }
}
