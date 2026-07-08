using System;
using System.IO;
using System.Linq;
using System.Security.Claims;
using System.Threading.Tasks;
using AIAugmentedPitchAnalyzer.Application.DTOs.Pitch;
using AIAugmentedPitchAnalyzer.Application.Interfaces.IServices;
using AIAugmentedPitchAnalyzer.Shared.Responses;
using AutoMapper;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;

namespace AIAugmentedPitchAnalyzer.Api.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class PitchController : ControllerBase
    {
        private readonly IPitchService _pitchService;
        private readonly IWebHostEnvironment _env;

        public PitchController(IPitchService pitchService, IWebHostEnvironment env)
        {
            _pitchService = pitchService;
            _env = env;
        }

        [HttpPost("upload")]
        [Authorize]
        public async Task<IActionResult> UploadWithFile([FromForm] UploadPitchWithFileRequest request)
        {
            if (request == null || request.File == null || request.File.Length == 0)
            {
                return BadRequest(new ApiResponse<PitchDto> { Success = false, Message = "A pitch file is required." });
            }

            var fileExtension = Path.GetExtension(request.File.FileName).ToLowerInvariant();
            var supportedExtensions = new[] { ".pdf", ".pptx" };
            if (!supportedExtensions.Contains(fileExtension))
            {
                return BadRequest(new ApiResponse<PitchDto> { Success = false, Message = "Only PDF and PPTX pitch deck files are supported." });
            }

            var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value ?? User.FindFirst("sub")?.Value;
            if (!Guid.TryParse(userIdClaim, out var userId))
            {
                return Unauthorized(new ApiResponse<PitchDto> { Success = false, Message = "Invalid or missing user identity." });
            }

            var storagePath = Path.Combine(_env.ContentRootPath, "uploads", "pitch-decks");

            var uploadRequest = new UploadPitchRequest
            {
                StartupId = request.StartupId,
                Title = string.IsNullOrWhiteSpace(request.Title) ? "Pitch Deck" : request.Title.Trim(),
            };

            var result = await _pitchService.UploadPitchWithFileAsync(
                uploadRequest,
                request.File.OpenReadStream(),
                request.File.FileName,
                request.File.ContentType ?? "application/octet-stream",
                request.File.Length,
                userId,
                storagePath);

            if (!result.Success || result.Data == null)
            {
                return BadRequest(result);
            }

            return CreatedAtAction(nameof(GetById), new { id = result.Data.Id }, result);
        }

        [HttpGet]
        [Authorize]
        public async Task<IActionResult> GetAll([FromQuery] Guid? startupId = null)
        {
            var result = startupId.HasValue
                ? await _pitchService.GetPitchesByStartupAsync(startupId.Value)
                : await _pitchService.GetAllPitchesAsync();

            return Ok(result);
        }

        [HttpGet("{id}")]
        [Authorize]
        public async Task<IActionResult> GetById(Guid id)
        {
            var result = await _pitchService.GetPitchAsync(id);
            if (!result.Success)
            {
                return NotFound(result);
            }

            return Ok(result);
        }
    }

    public class UploadPitchWithFileRequest
    {
        public Guid StartupId { get; set; }
        public string Title { get; set; } = "Pitch Deck";
        public IFormFile? File { get; set; }
    }
}
