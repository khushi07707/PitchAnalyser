namespace AIAugmentedPitchAnalyzer.Shared.Settings
{
    public class AISettings
    {
        public string Provider { get; set; } = "Local";
        public string Model { get; set; } = "gpt-4o-mini";
        public string? ApiKey { get; set; }
        public string? Endpoint { get; set; }
        public string? ApiVersion { get; set; }
    }
}
