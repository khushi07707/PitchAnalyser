using System;

namespace AIAugmentedPitchAnalyzer.Application.DTOs.Pitch
{
    public class UploadPitchRequest
    {
        public Guid StartupId { get; set; }
        public string Title { get; set; } = "Pitch Deck";
        // File upload will be handled by controller as IFormFile; metadata here.
        public Guid? FileRecordId { get; set; }
    }
}
