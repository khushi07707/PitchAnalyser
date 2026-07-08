namespace AIAugmentedPitchAnalyzer.Application.DTOs.Auth
{
    public class RegisterRequest
    {
        public string FirstName { get; set; } = null!;
        public string? LastName { get; set; }
        public string Email { get; set; } = null!;
        public string Password { get; set; } = null!;
    }
}
