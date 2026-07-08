using AIAugmentedPitchAnalyzer.Application.DTOs.Auth;
using AIAugmentedPitchAnalyzer.Application.Interfaces.IServices;
using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;

namespace AIAugmentedPitchAnalyzer.Api.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AuthController : ControllerBase
    {
        private readonly IAuthService _authService;

        public AuthController(IAuthService authService)
        {
            _authService = authService;
        }

        [HttpPost("register")]
        public async Task<IActionResult> Register([FromBody] RegisterRequest request)
        {
            var result = await _authService.RegisterAsync(request);
            return CreatedAtAction(nameof(Register), new { email = result.Email }, result);
        }

        [HttpPost("login")]
        public async Task<IActionResult> Login([FromBody] LoginRequest request)
        {
            var res = await _authService.LoginAsync(request);
            if (res == null) return Unauthorized(new { message = "Invalid credentials" });
            return Ok(res);
        }
    }
}
