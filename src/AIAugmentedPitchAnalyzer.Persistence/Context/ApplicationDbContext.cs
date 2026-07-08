using AIAugmentedPitchAnalyzer.Domain.Entities;
using AIAugmentedPitchAnalyzer.Domain.Enums;
using Microsoft.EntityFrameworkCore;

namespace AIAugmentedPitchAnalyzer.Persistence.Context
{
    /// <summary>
    /// EF Core database context for the application.
    /// </summary>
    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options) : base(options)
        {
        }

        public DbSet<User> Users => Set<User>();
        public DbSet<Role> Roles => Set<Role>();
        public DbSet<Startup> Startups => Set<Startup>();
        public DbSet<FinancialData> FinancialDatas => Set<FinancialData>();
        public DbSet<Pitch> Pitches => Set<Pitch>();
        public DbSet<PitchAnalysis> PitchAnalyses => Set<PitchAnalysis>();
        public DbSet<FileRecord> FileRecords => Set<FileRecord>();

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            // Roles
            modelBuilder.Entity<Role>(b =>
            {
                b.ToTable("roles");
                b.HasKey(x => x.Id);
                b.Property(x => x.Name).IsRequired().HasMaxLength(100);
                b.HasIndex(x => x.Name).IsUnique();
            });

            // Users
            modelBuilder.Entity<User>(b =>
            {
                b.ToTable("users");
                b.HasKey(x => x.Id);
                b.Property(x => x.Email).IsRequired().HasMaxLength(256);
                b.HasIndex(x => x.Email).IsUnique();
                b.HasOne(x => x.Role).WithMany(r => r.Users).HasForeignKey(x => x.RoleId).OnDelete(DeleteBehavior.Restrict);
            });

            // Startups
            modelBuilder.Entity<Startup>(b =>
            {
                b.ToTable("startups");
                b.HasKey(x => x.Id);
                b.Property(x => x.Name).IsRequired().HasMaxLength(200);
                b.Property(x => x.BusinessDescription).IsRequired();
                b.Property(x => x.WebsiteUrl).HasMaxLength(500);
                b.Property(x => x.Industry).HasConversion<int>();
                b.Property(x => x.FundingStage).HasConversion<int>();
                b.HasOne(x => x.CreatedBy).WithMany(u => u.Startups).HasForeignKey(x => x.CreatedById).OnDelete(DeleteBehavior.SetNull);
            });

            // FinancialData
            modelBuilder.Entity<FinancialData>(b =>
            {
                b.ToTable("financial_data");
                b.HasKey(x => x.Id);
                b.HasOne(x => x.Startup).WithOne(s => s.FinancialData).HasForeignKey<FinancialData>(x => x.StartupId).OnDelete(DeleteBehavior.Cascade);
            });

            // FileRecord
            modelBuilder.Entity<FileRecord>(b =>
            {
                b.ToTable("file_records");
                b.HasKey(x => x.Id);
                b.Property(x => x.FilePath).IsRequired();
                b.Property(x => x.ContentType).HasMaxLength(200);
                b.HasOne(x => x.UploadedBy).WithMany(u => u.UploadedFiles).HasForeignKey(x => x.UploadedById).OnDelete(DeleteBehavior.SetNull);
            });

            // Pitch
            modelBuilder.Entity<Pitch>(b =>
            {
                b.ToTable("pitches");
                b.HasKey(x => x.Id);
                b.Property(x => x.Title).HasMaxLength(300);
                b.Property(x => x.ExtractedText).HasColumnType("text");
                b.HasOne(x => x.Startup).WithMany(s => s.Pitches).HasForeignKey(x => x.StartupId).OnDelete(DeleteBehavior.Cascade);
                b.HasOne(x => x.FileRecord).WithOne(f => f.Pitch).HasForeignKey<Pitch>(x => x.FileRecordId).OnDelete(DeleteBehavior.SetNull);
            });

            // PitchAnalysis
            modelBuilder.Entity<PitchAnalysis>(b =>
            {
                b.ToTable("pitch_analyses");
                b.HasKey(x => x.Id);
                b.Property(x => x.AnalysisJson).IsRequired();
                b.HasOne(x => x.Pitch).WithOne(p => p.Analysis).HasForeignKey<PitchAnalysis>(x => x.PitchId).OnDelete(DeleteBehavior.Cascade);
            });

            // Convert all table, column, key, and constraint names to lowercase
            foreach (var entity in modelBuilder.Model.GetEntityTypes())
            {
                entity.SetTableName(entity.GetTableName()?.ToLowerInvariant());

                foreach (var property in entity.GetProperties())
                {
                    property.SetColumnName(property.GetColumnName().ToLowerInvariant());
                }

                foreach (var key in entity.GetKeys())
                {
                    key.SetName(key.GetName()?.ToLowerInvariant());
                }

                foreach (var fk in entity.GetForeignKeys())
                {
                    fk.SetConstraintName(fk.GetConstraintName()?.ToLowerInvariant());
                }

                foreach (var index in entity.GetIndexes())
                {
                    index.SetDatabaseName(index.GetDatabaseName()?.ToLowerInvariant());
                }
            }
        }
    }
}
