using AIAugmentedPitchAnalyzer.Application.Interfaces.IServices;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System;
using System.IO;
using System.Security.Claims;
using System.Threading.Tasks;

namespace AIAugmentedPitchAnalyzer.Api.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class FilesController : ControllerBase
    {
        private readonly IFileService _fileService;
        private readonly IWebHostEnvironment _env;

        public FilesController(IFileService fileService, IWebHostEnvironment env)
        {
            _fileService = fileService;
            _env = env;
        }

        [HttpPost("upload")]
        [Authorize]
        public async Task<IActionResult> Upload()
        {
            var file = Request.Form.Files.Count > 0 ? Request.Form.Files[0] : null;
            if (file == null || file.Length == 0) return BadRequest(new { Message = "No file provided" });

            var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier) ?? User.FindFirst("sub");
            if (userIdClaim == null) return Unauthorized();
            if (!Guid.TryParse(userIdClaim.Value, out var userId)) return Unauthorized();

            var storagePath = Path.Combine(_env.ContentRootPath, "uploads");

            using (var stream = file.OpenReadStream())
            {
                var result = await _fileService.UploadFileAsync(stream, file.FileName, file.ContentType, file.Length, userId, storagePath);
                if (!result.Success) return BadRequest(new { result.Message });
                return Ok(result);
            }
        }

        [HttpGet("{id}")]
        [Authorize]
        public async Task<IActionResult> Get(Guid id)
        {
            var result = await _fileService.GetFileAsync(id);
            if (!result.Success) return NotFound(new { result.Message });
            return Ok(result);
        }

        [HttpGet("{id}/download")]
        [Authorize]
        public async Task<IActionResult> Download(Guid id)
        {
            var result = await _fileService.GetFileAsync(id);
            if (!result.Success || result.Data == null) return NotFound(new { result.Message });

            if (!System.IO.File.Exists(result.Data.FilePath))
            {
                return NotFound(new { Message = "Stored file not found." });
            }

            return PhysicalFile(result.Data.FilePath, result.Data.ContentType ?? "application/octet-stream", result.Data.FileName);
        }

        [HttpGet("{id}/extract")]
        [Authorize]
        public async Task<IActionResult> Extract(Guid id)
        {
            var result = await _fileService.ExtractTextAsync(id);
            if (!result.Success) return NotFound(new { result.Message });
            return Ok(result);
        }
    }
}
