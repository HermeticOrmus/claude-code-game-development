---
name: unreal-patterns
description: "Unreal Engine 5 C++ patterns: an ACharacter subclass with Enhanced Input, Blueprint interfaces, server RPCs for player actions, and Gameplay Tags. Use when writing gameplay code in Unreal C++."
---

# Unreal Patterns

## ACharacter Subclass with Enhanced Input

```cpp
// MyCharacter.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "InputActionValue.h"
#include "MyCharacter.generated.h"

class UInputMappingContext;
class UInputAction;

UCLASS()
class MYGAME_API AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyCharacter();

protected:
    virtual void BeginPlay() override;
    virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

    // Input actions - set in Blueprint or C++ defaults
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
    TObjectPtr<UInputMappingContext> DefaultMappingContext;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
    TObjectPtr<UInputAction> MoveAction;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
    TObjectPtr<UInputAction> JumpAction;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
    TObjectPtr<UInputAction> LookAction;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stats")
    float MaxHealth = 100.f;

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Stats")
    float CurrentHealth;

    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;

private:
    void Move(const FInputActionValue& Value);
    void Look(const FInputActionValue& Value);
};
```

```cpp
// MyCharacter.cpp
#include "MyCharacter.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "Net/UnrealNetwork.h"

AMyCharacter::AMyCharacter()
{
    PrimaryActorTick.bCanEverTick = false;  // Disable if unused
    bReplicates = true;
    CurrentHealth = MaxHealth;
}

void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();

    if (APlayerController* PC = Cast<APlayerController>(Controller))
    {
        if (UEnhancedInputLocalPlayerSubsystem* Subsystem =
            ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PC->GetLocalPlayer()))
        {
            Subsystem->AddMappingContext(DefaultMappingContext, 0);
        }
    }
}

void AMyCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    if (UEnhancedInputComponent* EIC = Cast<UEnhancedInputComponent>(PlayerInputComponent))
    {
        EIC->BindAction(JumpAction, ETriggerEvent::Started, this, &ACharacter::Jump);
        EIC->BindAction(JumpAction, ETriggerEvent::Completed, this, &ACharacter::StopJumping);
        EIC->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AMyCharacter::Move);
        EIC->BindAction(LookAction, ETriggerEvent::Triggered, this, &AMyCharacter::Look);
    }
}

void AMyCharacter::Move(const FInputActionValue& Value)
{
    FVector2D MoveVector = Value.Get<FVector2D>();
    if (Controller)
    {
        const FRotator YawRotation(0, Controller->GetControlRotation().Yaw, 0);
        AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X), MoveVector.Y);
        AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y), MoveVector.X);
    }
}

void AMyCharacter::Look(const FInputActionValue& Value)
{
    FVector2D LookAxis = Value.Get<FVector2D>();
    AddControllerYawInput(LookAxis.X);
    AddControllerPitchInput(LookAxis.Y);
}

void AMyCharacter::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(AMyCharacter, CurrentHealth);
}
```

## Blueprint Interface Pattern

```cpp
// BPI_Interactable.h - Define interaction interface in C++, implement in Blueprint
#pragma once
#include "CoreMinimal.h"
#include "UObject/Interface.h"
#include "BPI_Interactable.generated.h"

UINTERFACE(MinimalAPI, BlueprintType)
class UInteractable : public UInterface
{
    GENERATED_BODY()
};

class MYGAME_API IInteractable
{
    GENERATED_BODY()
public:
    // BlueprintNativeEvent: C++ default + Blueprint can override
    UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category = "Interaction")
    void Interact(APlayerController* Interactor);

    UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category = "Interaction")
    FText GetInteractionPrompt();
};
```

```cpp
// PlayerController - detect and call interface without casting to concrete type
void AMyPlayerController::TryInteract()
{
    // Line trace from camera
    FHitResult Hit;
    FVector Start = PlayerCameraManager->GetCameraLocation();
    FVector End = Start + PlayerCameraManager->GetCameraRotation().Vector() * 300.f;

    if (GetWorld()->LineTraceSingleByChannel(Hit, Start, End, ECC_Visibility))
    {
        if (AActor* HitActor = Hit.GetActor())
        {
            // Execute interface without hard cast - works on any Blueprint implementing it
            if (HitActor->Implements<UInteractable>())
            {
                IInteractable::Execute_Interact(HitActor, this);
            }
        }
    }
}
```

## Server RPC for Player Actions

```cpp
// Attack action: client requests, server validates and applies
// In character header:
UFUNCTION(Server, Reliable, WithValidation)
void ServerRequestAttack(FVector TargetLocation);

// In character source:
bool AMyCharacter::ServerRequestAttack_Validate(FVector TargetLocation)
{
    // Basic validation: is target within possible attack range?
    return FVector::Distance(GetActorLocation(), TargetLocation) < 1000.f;
}

void AMyCharacter::ServerRequestAttack_Implementation(FVector TargetLocation)
{
    // Only runs on server - safe to modify game state
    if (!HasAuthority()) return;

    // Apply damage to any actors in radius
    TArray<AActor*> HitActors;
    UGameplayStatics::GetAllActorsInRadius(this, TargetLocation, 200.f, HitActors);
    for (AActor* Actor : HitActors)
    {
        UGameplayStatics::ApplyDamage(Actor, 25.f, GetController(), this, nullptr);
    }

    // Multicast visual effect to all clients
    MulticastPlayAttackEffect(TargetLocation);
}

UFUNCTION(NetMulticast, Unreliable)
void MulticastPlayAttackEffect(FVector Location);

void AMyCharacter::MulticastPlayAttackEffect_Implementation(FVector Location)
{
    // Cosmetic only - spawn particles, play sound
    UGameplayStatics::SpawnEmitterAtLocation(GetWorld(), AttackParticle, Location);
}
```

## Gameplay Tag Usage

```cpp
// Using FGameplayTag instead of enums for ability/status classification
#include "GameplayTagContainer.h"

// In GameplayTags.h - declare native tags
UE_DECLARE_GAMEPLAY_TAG_EXTERN(TAG_Ability_Jump)
UE_DECLARE_GAMEPLAY_TAG_EXTERN(TAG_Status_Stunned)
UE_DECLARE_GAMEPLAY_TAG_EXTERN(TAG_DamageType_Fire)

// In GameplayTags.cpp
UE_DEFINE_GAMEPLAY_TAG(TAG_Ability_Jump, "Ability.Jump")
UE_DEFINE_GAMEPLAY_TAG(TAG_Status_Stunned, "Status.Stunned")
UE_DEFINE_GAMEPLAY_TAG(TAG_DamageType_Fire, "DamageType.Fire")

// Usage: check status
bool AMyCharacter::IsStunned() const
{
    if (UAbilitySystemComponent* ASC = GetAbilitySystemComponent())
    {
        return ASC->HasMatchingGameplayTag(TAG_Status_Stunned);
    }
    return false;
}
```

## Anti-Patterns

- **Game logic in `Tick`**: `Tick` runs every frame. Move non-frame-critical logic to timers (`FTimerManager::SetTimer`) or events. Always profile before leaving logic in Tick.
- **Cast everywhere for communication**: `Cast<AMyPlayer>(OtherActor)->DoThing()` couples systems. Use Blueprint Interfaces for loose coupling - any actor can implement the interface without the caller knowing the concrete type.
- **Replication on everything**: `UPROPERTY(Replicated)` has bandwidth cost. Only replicate what clients need to display. Movement is auto-replicated by CharacterMovementComponent. Don't re-replicate it.
- **Logic in GameMode run on clients**: GameMode only exists on server. Client-side code that accesses `GetGameMode()` returns null. Client-visible game state goes in GameState.
- **`GetAllActorsOfClass` in Tick**: Iterates all actors in the world every frame. Cache results, subscribe to spawn/destroy events, or use TActorIterator once at BeginPlay.
- **Forgetting `IsValid()`**: UObjects can be garbage collected. `ptr != nullptr` is not enough. Always use `IsValid(ptr)` in UE.
