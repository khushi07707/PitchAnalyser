namespace AIAugmentedPitchAnalyzer.Shared.Settings
{
    /// <summary>
    /// JWT settings bound from configuration.
    /// </summary>
    public class JwtSettings
    {
        public string Secret { get; set; } = "replace_with_long_secret_in_production";
        public string Issuer { get; set; } = "AIAugmentedPitchAnalyzer";
        public string Audience { get; set; } = "AIAugmentedPitchAnalyzerClient";
        public int ExpiresMinutes { get; set; } = 60;
    }
}
